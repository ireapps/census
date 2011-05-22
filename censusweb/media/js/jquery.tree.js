// Require jQuery
// Use jQuery.cookie if you want to restore the previous expansion of the tree

jQuery.fn.tree = function(options) {

  // Setup default options
  /** Avaiable options are:
   *  - open_char: defeault character to display on open node in tree
   *  - close_char: defeault character to display on close node in tree
   *  - default_expanded_paths_string: if no cookie found the tree will be expand with this paths string
  **/
  if(options === undefined || options === null)
    options = {};
  var open_char = options.open_char;
  var close_char = options.close_char;
  var default_expanded_paths_string = options.default_expanded_paths_string;
  if(open_char === undefined || open_char === null)
    open_char = '&#9660;';
  if(close_char === undefined || close_char === null)
    close_char = '&#9658;';
  if(default_expanded_paths_string === undefined || default_expanded_paths_string === null)
    default_expanded_paths_string = '0';

  // Get the expanded paths from the current state of tree
  jQuery.fn.save_paths = function() {
    var paths = [];
    var path = [];
    var open_nodes = jQuery(this).find('li span.open');
    var last_depth = null;
    for(var i = 0; i < open_nodes.length; i++) {
      var depth = jQuery(open_nodes[i]).parents('ul').length-1;
      if((last_depth == null && depth > 0) || (depth > last_depth && depth-last_depth > 1))
        continue;
      var pos = jQuery(open_nodes[i]).parent().prevAll().length;
      if(last_depth == null) {
        path = [pos];
      } else if(depth < last_depth) {
        paths.push(path.join('/'));
        var diff = last_depth - depth;
        path.splice(path.length-diff-1, diff+1);
        path.push(pos);
      } else if(depth == last_depth) {
        paths.push(path.join('/'));
        path.splice(path.length-1, 1);
        path.push(pos);
      } else if(depth > last_depth) {
        path.push(pos);
      }
      last_depth = depth;
    }
    paths.push(path.join('/'));
    try { jQuery.cookie(this.attr('class'), paths.join(',')); }
    catch(e) {}
  };

  // This function expand the tree with 'path'
  jQuery.fn.restore_paths = function() {
    var paths_string = null;
    try { paths_string = jQuery.cookie(this.attr('class')); }
    catch(e) { paths_string = default_expanded_paths_string; }
    if(paths_string === null || paths_string === undefined)
      paths_string = default_expanded_paths_string;
    var paths = paths_string.split(',');
    for(var i = 0; i < paths.length; i++) {
      var path = paths[i].split('/');
      var obj = jQuery(this);
      for(var j = 0; j < path.length; j++) {
        obj = jQuery(obj.children('li')[path[j]]);
        obj.children('span').attr('class', 'open');
        obj.children('span').html(open_char);
        obj = obj.children('ul')
        obj.show();
      }
    }
  };

  for(var i = 0; i < this.length; i++) {
    if(this[i].tagName === 'UL') {
      // Make a tree
      jQuery(this[i]).find('li').has('ul').prepend('<span class="close" style="cursor:pointer;">' + close_char + '</span>');
      jQuery(this[i]).find('ul').hide();
      // Restore cookie expand path
      jQuery(this[i]).restore_paths();
      // Click event
      jQuery(this[i]).find('span').live('click', {tree : this[i]}, function(e) {
        if (jQuery(this).attr('class') == 'open') {
          jQuery(this).parent().children('ul').hide('slow');
          jQuery(this).attr('class', 'close');
          jQuery(this).html(close_char);
        } else if (jQuery(this).attr('class') == 'close') {
          jQuery(this).parent().children('ul').show('slow');
          jQuery(this).attr('class', 'open');
          jQuery(this).html(open_char);
        }
        jQuery(e.data.tree).save_paths();
      });
    }
  }
}