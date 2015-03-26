/*globals define*/
define([
  'jquery',
  'underscore',
  'tpl!teal/options-row.erb.html',
  'tpl!teal/options-value-row.erb.html'
], function ($, _, optionRowTemplate, valueRowTemplate) {
  // This module handles the product options admin interface.

  "use strict";

  function OptionWidget(selector) {
    this.$container = $(selector);
    this
      .proxy('optionAddHandler')
      .proxy('valueAddHandler')
      .proxy('optionRemoveHandler')
      .proxy('valueRemoveHandler')
      .proxy('optionGrabHandler')
      .proxy('valueGrabHandler')
      .proxy('setGravity');
    this.init();
  }

  OptionWidget.prototype = {

    proxy: function(meth) {
      // Bind a method so that it always gets the image widget instance for
      // ``this``. Return ``this`` so chaining calls works.
      this[meth] = $.proxy(this[meth], this);
      return this;
    },

    init: function() {
      this.$container
        .on('click', '.js-option-remove', this.optionRemoveHandler)
        .on('click', '.js-value-remove', this.valueRemoveHandler)
        .on('click', '.js-option-add', this.optionAddHandler)
        .on('click', '.js-value-add', this.valueAddHandler)
        .on('mousedown', '.js-option-drag-handle', this.optionGrabHandler)
        .on('mousedown', '.js-value-drag-handle', this.valueGrabHandler);
    },

    optionAddHandler: function(e) {
      console.log("option add");
      e.preventDefault();
      e.stopPropagation();

      var $optionsBody = this.$container.find('> tbody'),
          $options = $optionsBody.find('> tr'),
          nextIndex = $options.length,
          newID = 'new-' + nextIndex;

      // Make a new row, passing in the ID
      var $el = $(optionRowTemplate({
        idx: nextIndex,
        gravity: nextIndex,
        id: newID
      }));
      $optionsBody.append($el);

      var $optionEl = $(valueRowTemplate({
        optionIdx: nextIndex,
        valueIdx: 0,
        gravity: 0,
        id: 'new-0'
      }));
      $el.find('table > tbody').append($optionEl);
      $optionEl.find('input[type=radio]').prop('checked', 'checked');

    },

    optionRemoveHandler: function(e) {
      console.log("option remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('tr').remove();
    },

    optionGrabHandler: function(e) {
      console.log("option grab");

    },

    optionDragHandler: function(e) {
      console.log("option drag");

    },

    optionDropHandler: function(e) {
      console.log("option drop");

    },

    valueAddHandler: function(e) {
      console.log("value add");
      e.preventDefault();
      e.stopPropagation();

      var $el = $(e.target),
          $thisOption = $el.closest('table').closest('tr');

      var $optionsBody = this.$container.find('> tbody'),
          $options = $optionsBody.find('> tr'),
          optionIdx = $options.index($thisOption);

      var $valuesBody = $el.closest('table').find('> tbody'),
          $values = $valuesBody.find('> tr'),
          nextIndex = $values.length,
          newID = 'new-' + nextIndex;

      $valuesBody.append(valueRowTemplate({
        optionIdx: optionIdx,
        valueIdx: nextIndex,
        gravity: nextIndex,
        id: newID
      }));
    },

    valueRemoveHandler: function(e) {
      console.log("value remove");
      e.preventDefault();
      e.stopPropagation();
      $(e.target).closest('tr').remove();

      // XXX Ideally this should update the option's default to a new value.
    },

    valueGrabHandler: function(e) {
      console.log("value grab");

    },

    valueDragHandler: function(e) {
      console.log("value drag");

    },

    valueDropHandler: function(e) {
      console.log("value drop");

    },

    setGravity: function(e) {
      console.log("set gravity");
    }

  };

  $(function () {
    $('.js-option-widget').each(function() {
      var d = new OptionWidget(this);
    });
  });
});
