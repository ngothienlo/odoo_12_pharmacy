odoo.define('kingsport_module.KanbanController', function (require) {
"use strict";

/**
 * The KanbanController is the class that coordinates the kanban model and the
 * kanban renderer.  It also makes sure that update from the search view are
 * properly interpreted.
 */

    var KanbanController = require('web.KanbanController');
    var viewUtils = require('web.viewUtils');
    var view_dialogs = require('web.view_dialogs');
    var core = require('web.core');

    var _t = core._t;

    KanbanController.include({

        /**
         * @private
         * @param {OdooEvent} ev
         * @param {KanbanColumn} ev.target the column in which the record should
         *   be added
         * @param {Object} ev.data.values the field values of the record to
         *   create; if values only contains the value of the 'display_name', a
         *   'name_create' is performed instead of 'create'
         * @param {function} [ev.data.onFailure] called when the quick creation
         *   failed
         */
        _onQuickCreateRecord: function (ev) {
            var self = this;
            var values = ev.data.values;
            var column = ev.target;
            var onFailure = ev.data.onFailure || function () {};

            // function that updates the kanban view once the record has been added
            // it receives the local id of the created record in arguments
            var update = function (db_id) {
                self._updateEnv();

                var columnState = self.model.getColumn(db_id);
                var state = self.model.get(self.handle);
                return self.renderer
                    .updateColumn(columnState.id, columnState, {openQuickCreate: true, state: state})
                    .then(function () {
                        if (ev.data.openRecord) {
                            self.trigger_up('open_record', {id: db_id, mode: 'edit'});
                        }
                    });
            };

            this.model.createRecordInGroup(column.db_id, values)
            .then(update)
            .fail(function (error, ev) {
                ev.preventDefault();
                var columnState = self.model.get(column.db_id, {raw: true});
                var context = columnState.getContext();
                var state = self.model.get(self.handle, {raw: true});
                var groupedBy = state.groupedBy[0];
                context['default_' + groupedBy] = viewUtils.getGroupValue(columnState, groupedBy);
                var default_vals = {default_name: values.name || values.display_name};
                if(state.model === 'crm.lead'){
                    default_vals['default_partner_id'] = values.partner_id || false;
                    $.when(
                        self._rpc({
                            model: state.model,
                            method: 'get_formview_id_on_kanban',
                            context: context,
                        }),
                        self._rpc({
                            model: state.model,
                            method: 'check_access_rights',
                            kwargs: {operation: 'create', raise_exception: false}
                        }),
                        // self._rpc({
                        //     model: state.model,
                        //     method: 'get_values_for_kanban',
                        //     kwargs: {values: values},
                        // }),
                    ).then(function (view_id, write_access) {
                        new view_dialogs.FormViewDialog(self, {
                            res_model: state.model,
                            context: _.extend(default_vals, context),
                            title: _t("Create"),
                            view_id: view_id,
                            disable_multiple_selection: true,
                            on_saved: function (record) {
                                self.model.addRecordToGroup(column.db_id, record.res_id)
                                    .then(update);
                            },
                        }).open().opened(onFailure);
                    })
                } else {
                    new view_dialogs.FormViewDialog(self, {
                        res_model: state.model,
                        context: _.extend(default_vals, context),
                        title: _t("Create"),
                        disable_multiple_selection: true,
                        on_saved: function (record) {
                            self.model.addRecordToGroup(column.db_id, record.res_id)
                                .then(update);
                        },
                    }).open().opened(onFailure);
                }
            });
        },
    });

});
