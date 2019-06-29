odoo.define("crm_activity.Activity", function(require) {
  "use strict";
  var core = require("web.core");
  var Activity = require("mail.Activity");
  var _t = core._t;

  Activity.include({
    /**
     * @private
     * @param {Object} fieldsToReload
     */
    _reload: function (fieldsToReload) {
      var res = this._super.apply(this, arguments);
      /**
       * Customize here, because in if put activity_ids in form
       * view can't call reload from parent (Chatter widget). So here, we try
       * call chatter onchange manually
       * we only do this in case parent is a Form view to avoid other side-effect
       */
      var parent = this.getParent();
      if (parent && parent.viewType === 'form' && parent.chatter) {
        parent.chatter.trigger_up('reload_mail_fields', fieldsToReload);
      }
    },
    _onMarkActivityDone: function(ev) {
      ev.preventDefault();
      var res_model = this.model;

      /* Open form like _onEditActivity method does*/
      if (res_model === "crm.lead") {
        var activityID = $(ev.currentTarget).data("activity-id");
        this._openActivityDoneForm(
          activityID,
          this._reload.bind(this, { activity: true, thread: true })
        );
      } else {
        this._super.apply(this, arguments);
      }
    },
    _openActivityDoneForm: function(id, callback) {
      var self = this;
      self
        ._rpc({
          model: "ir.model.data",
          method: "xmlid_to_object",
          args: ["crm_activity.mail_activity_done_view_form_popup"]
        })
        .done(function(view) {
          var view_ids = (view || "").match(/\d+/);
          var view_id = parseInt(view_ids[0]) || false;
          var action = {
            name: _t("Mark Activity Done"),
            type: "ir.actions.act_window",
            res_model: "mail.activity",
            view_mode: "form",
            view_type: "form",
            views: [[view_id, "form"]],
            target: "new",
            context: {
              default_res_id: self.res_id,
              default_res_model: self.model
            },
            res_id: id || false
          };
          return self.do_action(action, { on_close: callback });
        });
    }
  });
});
