from pathlib import Path

class EFCObservability(BaseComposite):

    def compose(self):
        self.provider = f"influxdb-{self.spec.influxdbInstance}"
        # create grafana folder
        folder_uid = self.create_folder()
        # create grafana datasource
        datasource_uid = self.get_ds_uid()
        self.create_dashboard(folder_uid)
        self.create_rule_group(datasource_uid)

    def create_folder(self):
        folder = self.resources.folder('oss.grafana.crossplane.io/v1alpha1', 'Folder')
        folder.metadata.labels.cluster = self.environment.cluster.name
        folder.spec.providerConfigRef.name = self.provider
        folder.spec.forProvider.title = self.spec.title
        return folder.status.atProvider.uid

    def create_dashboard(self, folder_uid):
        dashboard = self.resources.dashboard('oss.grafana.crossplane.io/v1alpha1', 'Dashboard')
        dashboard.metadata.name = self.spec.claimRef.name
        dashboard.metadata.labels.cluster = self.environment.cluster.name
        dashboard.spec.providerConfigRef.name = self.provider
        dashboard.spec.forProvider.folder = folder_uid
        dashboard.spec.forProvider.configJson = Path(__file__).with_name('dashboard.json').read_text()
        return dashboard.status.atProvider.uid

    def get_ds_uid(self):
        return self.requireds.datasource(
            'oss.grafana.crossplane.io/v1alpha1',
            'DataSource',
            name=f"influxdb-{self.spec.influxdbInstance}"
        )[0].status.atProvider.uid

    def create_rule_group(self, datasource_uid):
        rule_group = self.resources.rule_group('alerting.grafana.crossplane.io/v1alpha1', 'RuleGroup')
        rule_group.metadata.name = self.spec.claimRef.name
        rule_group.metadata.labels.cluster = self.environment.cluster.name
        rule_group.spec.providerConfigRef.name = self.provider
        rule_group.spec.forProvider.folderSelector.matchLabels.cluster = self.environment.cluster.name
        rule_group.spec.forProvider.intervalSeconds = 300
        for ix, spec in enumerate(self.spec.rules):
            self.create_rule(spec, rule_group.spec.forProvider.rule[ix], datasource_uid)

    def create_rule(self, spec, rule, datasource_uid):
        rule.name = spec.name
        rule.isPaused = True
        rule.execErrState = 'Alerting'
        rule['for'] = '2m'
        rule.noDataState = 'NoData'
        rule.condition = 'B'
        rule.annotations.summary = f"{spec.name} backlog above {spec.threshold} events"
        rule.annotations.description = f"{spec.name} backlog which determines the health of the processing pipeline"
        rule.annotations.__dashboardUid__ = 'ec19dcc4-17d1-4837-9a1c-8a31b7ef96e0'
        rule.annotations.__panelId__ = '3'
        rule.annotations.runbook_url = 'https://helpsystems.atlassian.net/wiki/spaces/FP/pages/185696827/Event+Fusion+Center+EFC'
        rule.labels.product = 'event-fusion-center'
        rule.labels.fta_application = self.environment.cluster.tags.map['FTA-application']
        rule.labels.fta_environment = self.environment.cluster.tags.map['FTA-environment']
        rule.labels.pagerduty = f"efc-{spec.severity}"
        rule.notificationSettings[0].contactPoint = f"efc-{spec.severity}"

        rule.data[0].datasourceUid = datasource_uid
        rule.data[0].refId ='A'
        rule.data[0].queryType = ''
        rule.data[0].relativeTimeRange[0]['from'] = 600
        rule.data[0].relativeTimeRange[0].to = 0
        model = Map()
        model.refId = 'A'
        model.resultFormat = 'time_series'
        model.interval = ''
        model.intervalFactor = 2
        model.query = ' |> '.join([
            'from(bucket: "fortra-efc")',
            'range(start: -5m)',
            'filter(fn: (r) => r["_measurement"] == "stream")',
            f'filter(fn: (r) => r["_field"] == "{spec.name.lower()}")',
            'aggregateWindow(every: 5m, fn: sum, createEmpty: false)',
            'last()',
        ])
        rule.data[0].model = format(model, 'json')

        rule.data[1].datasourceUid = '-100'
        rule.data[1].refId = 'B'
        rule.data[1].queryType = ''
        rule.data[1].relativeTimeRange[0]['from'] = 0
        rule.data[1].relativeTimeRange[0].to = 0
        model = Map()
        model.refId = 'B'
        model.type = 'classic_conditions'
        model.hide = False
        model.intervalMs = 1000
        model.maxDataPoints = 43200
        model.datasource.type = '__expr__'
        model.datasource.uid = '-100'
        model.conditions[0].type = 'query'
        model.conditions[0].query.params[0] = 'A'
        model.conditions[0].evaluator.type = 'gt'
        model.conditions[0].evaluator.params[0] = spec.threshold
        model.conditions[0].operator.type = 'and'
        model.conditions[0].reducer.type = 'last'
        rule.data[1].model = format(model, 'json')
