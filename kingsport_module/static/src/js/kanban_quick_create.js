odoo.define('kingsport_module.RecordQuickCreate', function (require) {
"use strict";

    var core = require('web.core');
    var RecordQuickCreate = require('web.kanban_record_quick_create');

    var QWeb = core.qweb;

    RecordQuickCreate.prototype.start = function () {
        this.$el.append(this.controller.$el);
        if(this.model==='crm.lead'){
            this.$el.append(QWeb.render('KanbanView.KingSport.RecordQuickCreate.buttons'));
        } else {
            this.$el.append(QWeb.render('KanbanView.RecordQuickCreate.buttons'));
        }

        // focus the first field
        this.controller.autofocus();

        // destroy the quick create when the user clicks outside
        core.bus.on('click', this, this._onWindowClicked);

        return true;
    };
});
