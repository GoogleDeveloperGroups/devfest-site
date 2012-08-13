/**
 * The Sexy Curls JQuery Plugin
 * By Elliott Kember - http://twitter.com/elliottkember
 * Released under the MIT license (MIT-LICENSE.txt)
 * 
 * My only request is: please don't over-use this plugin.
 * If this ends up being used all over the internets, and becomes "that annoying effect", I'll be upset.    
 *
 * I dragged a curl, and I liked it - I hope @jeresig don't mind it.
 */

(function($){
  $.fn.fold = function(options) {
    /* this doesn't work with IE8
    var ie55 = (navigator.appName == "Microsoft Internet Explorer" && parseInt(navigator.appVersion) == 4 && navigator.appVersion.indexOf("MSIE 5.5") != -1);
    var ie6 = (navigator.appName == "Microsoft Internet Explorer" && parseInt(navigator.appVersion) == 4 && navigator.appVersion.indexOf("MSIE 6.0") != -1);
    
    // We just won't show it for IE5.5 and IE6. Go away. I'm really tempted to write "document.location= 'http://www.getfirefox.com';" here.
    if (ie55 || ie6) {this.remove(); return true;}
    */
    
    // MSIE must be 8 or greater
    if (navigator.appName == "Microsoft Internet Explorer"){
        var ary = navigator.appVersion.match(/MSIE..../g);
        var msieVersion = 8; // in case our test fails try it anyway
        for(var i=0; i<ary.length; i++){
            msieVersion = parseInt(ary[i].substr(ary[i].indexOf(' ')+1));
            if (msieVersion > 7) break;
        }
        if (msieVersion < 8)  {this.remove(); return true;}
    }
  
    // New - you don't have to specify options!
    options = options || {};
    
    // Default awesomeness
    var defaults = {
      directory: '.',         // The directory we're in
      side: 'left',           // change me to "right" if you want rightness
      turnImage: 'fold.png',  // The triangle-shaped fold image
      maxHeight: 173,
      maxWidth: 160,// The maximum height. Duh.
      startingWidth:70,     // The height and width 
      startingHeight: 70,    // with which to start (these should probably be camelCase, d'oh.)
      autoCurl: true        // If this is set to true, the fold will curl/uncurl on mouseover/mouseout.
    };

    // Change turnImage if we're running the default image, and they've specified 'right'
    if (options.side == 'right' && !options.turnImage) defaults.turnImage = 'fold-sw.png';
  
    // Merge options with the defaults
    var options = $.extend(defaults, options);
    
    // Set up the wrapper objects
    var turn_hideme = $('<div id="turn_hideme">');
    var turn_wrapper = $('<div id="turn_wrapper">');
    var turn_object = $('<div id="turn_object">');
    var img = $('<img id="turn_fold" src="/images/fold-sw.png">');

    // Set starting width and height of our turn-o-ma-bob
    turn_object.css({
      width: options.startingWidth, 
      height: options.startingHeight
    });
  
    // There are different CSS considerations for a top-right fold.
    if (options.side == 'right') turn_wrapper.addClass('right');
  
    // Rappin', I'm rappin' - I'm rap-rap-rappin'.
    this.wrap(turn_wrapper).wrap(turn_object).after(img).wrap(turn_hideme);
    
    // If you want autoCurl, you don't get scrolling. Why? Because it looks silly.
    
    turn_wrapper = $('#turn_wrapper');
    turn_object = $('#turn_object');

    
    if (!options.autoCurl) {
      // Hit 'em with the drag-stick because it ain't gonna curl itself!
      turn_object.resizable({ 
        maxHeight: options.maxHeight, 
        aspectRatio: true,
        handles: options.side == 'left' ? 'se' : 'sw'
      });
    } else {
      // Thanks to @zzzrByte for this bit!
      turn_wrapper.hover(
        function(){
          turn_object.stop().animate({
            width: options.maxHeight,
            height: options.maxHeight
          },function(){
        	  
        		$('#turn_hideme').css("z-index","1200");
        	  
          });
        },
        function(){
          turn_object.stop().animate({
            width: options.startingHeight,
            height: options.startingHeight
          });
          
          $('#turn_hideme').css("z-index","0");
          
        }
      );
    }
  };
})(jQuery);
