/*
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
*/



/**
 * jQuery like object for use in Enasis Network projects.
 */
(function (global) {

  'use strict';

  global.$ = $;


  function $(selector) {

    if (!(this instanceof $))
      return new $(selector);


    if (!selector) {

      this.length = 0;
      this.elements = [];

      return this; }


    if (isquery(selector))
      return selector;

    else if (isnodes(selector))
      this.elements = selector;

    else if (isnode(selector))
      this.elements = [selector];

    else if (isstr(selector))
      _enquery(this, selector);


   this.length =
      this.elements
      .length;

    this.elements
      .forEach(
        (x, y) =>
        { this[y] = x; }); }


  $.prototype
    .enquery = true;

  $.prototype
    .each = _enquery_each;

  $.prototype
    .clone = _enquery_clone;

  $.prototype
    .css = _enquery_css;

  $.prototype
    .addClass = _enquery_addcls;

  $.prototype
    .remClass = _enquery_remcls;

  $.prototype
    .hide = _enquery_hide;

  $.prototype
    .show = _enquery_show;

  $.prototype
    .text = _enquery_text;

  $.prototype
    .html = _enquery_html;

  $.prototype
    .append = _enquery_append;

  $.prototype
    .replace = _enquery_replace;

  $.prototype
    .attr = _enquery_attr;

  $.prototype
    .prop = _enquery_prop;

})(window);



/**
 * Helper function for Enasis Network jQuery replacement.
 */
function _enquery(
  source,
  selector,
) {

  const create = /^<(\w+)\/>$/;

  assert(isstr(selector));

  if (!create.test(selector))
    source.elements =
      document
      .querySelectorAll(selector);

  else {

    let tagName =
      selector
      .match(create)[1];

    let element =
      document
      .createElement(tagName);

    source.elements = [element]; } }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_each(
  element,
) {

  let items = this.elements;

  this.elements.forEach(
    (x, y) =>
    element.call(x, y, x));

  return this; }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_css(
  name,
  value,
) {

  function _each() {
    this.style[name] = value; }

  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_addcls(
  name,
) {

  function _each() {
    this.classList
      .add(name); }

  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_remcls(
  name,
) {

  function _each() {
    this.classList
      .remove(name); }

  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_hide() {


  function _each() {

    let dataset = this.dataset;
    let style = this.style;
    let hide = dataset.enqHide;

    if (hide === undefined
        && style.display != 'none'
        && !isempty(style.display))
      dataset.enqHide =
        style.display;

    style.display = 'none'; }


  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_show() {


  function _each() {

    let dataset = this.dataset;
    let style = this.style;
    let hide = dataset.enqHide;

    if (hide !== undefined) {
      if (!isempty(hide))
        style.display = hide;
      else
        style
        .removeProperty('display');

      delete dataset.enqHide; }

    else
      style
      .removeProperty('display'); }


  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element
 *                   or the text value in first element.
 */
function _enquery_text(
  text,
) {

  if (text === undefined) {

    if (this.length > 0)
      return this[0].textContent;

    return undefined; }

  else {

    function _each() {
      this.textContent = text; }

    return this.each(_each); } }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element
 *                   or the HTML value in first element.
 */
function _enquery_html(
  html,
) {

  if (html === undefined) {

    if (this.length > 0)
      return this[0].innerHTML;

    return undefined; }

  else {

    if (isquery(html))
      html = html[0].outerHTML;

    else if (isnode(html))
      html = html.outerHTML;

    function _each() {
      this.innerHTML = html; }

    return this.each(_each); } }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_append(
  element,
) {

  assert(element.enquery)

  let nodes = element.elements;


  function _each(index) {

    nodes.forEach(
      (x) => {
        const element =
          index < 1 ?
          x : x.cloneNode(true);
        this
        .appendChild(element); }); }


  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_replace(
  element,
) {

  assert(element.enquery)

  let nodes = element.elements;


  function _each(index) {

    nodes.forEach(
      (x) => {
        const element =
          index < 1 ?
          x : x.cloneNode(true);
        this
        .replaceChildren(element); }); }


  return this.each(_each); }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element
 *                   or the attr value in first element.
 */
function _enquery_attr(
  name,
  value,
) {

  if (this.length === 0)
    return undefined;


  function _each() {
    if (value === null)
      this.removeAttribute(name);
    else
      this.setAttribute(
        name, value); }

  if (value !== undefined)
    return this.each(_each);


  let returned =
    this[0]
    .getAttribute(name);

  return returned; }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element
 *                   or the prop value in first element.
 */
function _enquery_prop(
  name,
  value,
) {

  if (this.length === 0)
    return undefined;


  function _each() {
    if (value === null)
      this.removeProperty(name);
    else
      this[name] = value; }

    if (value !== undefined)
      return this.each(_each);


  return this[0][name]; }



/**
 * Helper function for Enasis Network jQuery replacement.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function _enquery_clone() {

  let clones =
    Array
    .from(this.elements)
    .map(x => x.cloneNode(true));

  return $(clones); }
