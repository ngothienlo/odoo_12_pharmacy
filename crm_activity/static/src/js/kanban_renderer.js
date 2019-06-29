odoo.define('crm_activity.KanbanRenderer', function (require) {
  "use strict";

  var KanbanRenderer = require('web.KanbanRenderer');
  var KanbanColumn = require('web.KanbanColumn');
  var ColumnQuickCreate = require('web.kanban_column_quick_create');

  KanbanRenderer.include({
      _renderGrouped: function (fragment) {
          var model = this.__parentedParent && this.__parentedParent.modelName;
          if (model && model != 'crm.lead') {
            this._super.apply(this, arguments);
          }
          else {
            this._super.apply(this, arguments);
            // remove previous sorting
              if(this.$el.sortable('instance') !== undefined) {
                this.$el.sortable('destroy');
              }
          }
      }
      });
  });
