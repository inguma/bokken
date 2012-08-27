$(document).ready(function() {
    var bokken = $('#bokken');

    $.get('/bokken/file/name', '', function(data){
        $('#filename .content').text(data);
    }); // end get

    $.get('/bokken/file/dump', '', function(data){
        $('#asmdump .content').html(data);
    }); // end get

    $.get('/bokken/file/exports', '', function(data){
        $('#fileexports .content').html(data);
    }); // end get

    $.get('/bokken/file/imports', '', function(data){
        $('#fileimports .content').html(data);
    }); // end get

    $.get('/bokken/file/sections', '', function(data){
        $('#filesections .content').html(data);
    }); // end get

    $.get('/bokken/file/functions', '', function(data){
        $('#filefunctions .content').html(data);
    }); // end get
});
