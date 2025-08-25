/*
Functions and routines associated with Enasis Network Common Library.

This file is part of Enasis Network software eco-system. Distribution
is permitted, for more information consult the project license file.
*/



/**
 * Return the simple construct for SVG based icon images.
 *
 * @returns {Object} jQuery-like object for the element.
 */
function svgicon(
  image,
  dimension=null,
) {

  assert(!isnull(image));


  let element =
    $('<div/>').addClass(
      'encommon_svgicon');


  element.attr(
    'data-image',
    image);

  if (!isnull(dimension)) {

    element.css(
      'height',
      dimension);

    element.css(
      'width',
      dimension); }


  return element; }
