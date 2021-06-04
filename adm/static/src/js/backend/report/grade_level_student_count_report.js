odoo.define('adm.report.grade_level_student_count_report', require => {
    "use strict";
    const GraphRenderer = require('web.GraphRenderer');
    const {_t} = require('web.core');
    GraphRenderer.include({

        /**
         * @override
         * @param {Widget} parent
         * @param {Object} state
         * @param {Object} params
         * @param {boolean} [params.isEmbedded]
         * @param {Object} [params.fields]
         * @param {string} [params.title]
         * @constructor
         */
        init(parent, state, params) {
            this._super(...arguments);
            // if (parent && parent.state) {
            //     this.modelName = parent.state.model;
            // } else if (state.context.params) {
            //     this.modelName = state.context.params.model;
            // }
        },

        /**
         * This has the order and the list
         * @private
         */
        _getAdmissionLabelList() {
            return [
                'Inquiries',
                'Applications',
                'Next year enrolled',
                'Capacity',
                'Available',
            ]
        },

        _getStackedAdmissionLabelList() {
            return [
                'Inquiries',
                'Applications',
                'Next year enrolled',
                // 'Total Admissions\n (Inquiries + Applications)',
                // 'Total Prospect Students',
                // 'Next Year Enrolled',
                // 'Available',
            ]
        },

        _getAvailableLessList() {
            return [
                'Inquiries',
                'Applications',
                'Next year enrolled',
                // 'Total Admissions\n (Inquiries + Applications)',
                // 'Total Prospect Students',
                // 'Available',
            ]
        },
        _updateAdmDatasets(data) {
            if (this.state.mode === 'bar') {
                const stackedList = this._getStackedAdmissionLabelList();
                data = {
                    datasets: _.clone(data.datasets),
                    labels: _.clone(data.labels),
                };
                const availableDataset = {
                    label: _t("Available"),
                    originIndex: 1,
                    data: []
                }

                const capacityDataset = _.find(data.datasets, dataset => dataset.label === 'Capacity');
                availableDataset.data = _.clone(capacityDataset.data)

                data.datasets.push(availableDataset);

                const totalGradeLevelLabels = data.labels.length;
                const sortedList = this._getAdmissionLabelList();
                // I do really hate this solution...
                data.datasets = _.sortBy(data.datasets, (dataset) => sortedList.indexOf(dataset.label));
                data.datasets.forEach((dataset, index) => {
                    // used when stacked
                    dataset.stack = this.state.stacked && _.include(stackedList, dataset.label) ? this.state.origins[dataset.originIndex] : undefined;
                    dataset.backgroundColor = this._getColor(index);

                    const hidden = this.chart && this.chart.config.type === 'bar' ? this.chart.getDatasetMeta(index).hidden : null;
                    if (!hidden && _.include(this._getAvailableLessList(), dataset.label)) {
                        _.each(dataset.data, (v, i) => {
                            availableDataset.data[i] -= v;
                        });
                    }
                    // Theorically availableDataset will be always in the last position thanks to that datasets.push up
                    // So, this should be safe... I think...
                    dataset.data[totalGradeLevelLabels] = 0;
                    dataset.data[totalGradeLevelLabels] = _.reduce(dataset.data, (totalAccum, currentCount) => totalAccum + currentCount, 0);
                    dataset.hidden = hidden;
                });

                // Total Label
                data.labels.push(['Total'])
            }
            return data;
        },

        _renderAdmissionBarChart(dataPoints) {
            const self = this;
            // prepare data
            const data = this._prepareData(dataPoints);

            // prepare options
            const options = this._prepareOptions(data.datasets.length);
            options.legend.onClick = function(e, legendItem) {
                const index = legendItem.datasetIndex;
                const ci = this.chart;
                const meta = ci.getDatasetMeta(index);

                // See controller.isDatasetVisible comment
                meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;

                // We hid a dataset ... rerender the chart
                ci.update();
                this.chart.data = self._updateAdmDatasets(data);
                ci.update();
                ci.updateDatasets();
            }
            // create chart
            const ctx = document.getElementById(this.chartId);
            this.chart = new Chart(ctx, {
                type: 'bar',
                data: self._updateAdmDatasets(data),
                options: options,
            });
        },

        _renderBarChart(dataPoints) {
            // const storedAction = this.call('session_storage', 'getItem', 'current_action');
            // const lastAction = JSON.parse(storedAction || '{}');
            if (this.__parentedParent
                && this.__parentedParent.modelName === 'grade.level.student.count.report') {
                this._renderAdmissionBarChart(...arguments);
            } else {
                this._super(...arguments);
            }
        }
    })
});