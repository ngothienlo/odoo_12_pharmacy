odoo.define("crm_activity.AbstractController", function(require) {
  "use strict";

  var AbstractController = require('web.AbstractController');

  AbstractController.include({
        /**
     * Short helper method to reload the view
     *
     * @param {Object} [params] This object will simply be given to the update
     * @returns {Deferred}
     */
    reload: function (params) {
      if (this.modelName == 'crm.lead') {
        params = params || {};
        var fieldNames = params.fieldNames;
        if(fieldNames && Array.isArray(fieldNames)){
          fieldNames.push('stage_id', 'activity_history_count', 'probability');
        }
      }
      return this._super.apply(this, arguments);
    },

  });
});