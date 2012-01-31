<form method="POST" id="newcat" action="/tag" onsubmit="return getresult();">
	<textarea cols="80" rows="25" name="teks" id="teks"></textarea>
    <div class="formsection">
	<input type="submit" name="save" value="Tag"/>
    </div>
</form>
<div id="result" style="width:500px;background-color:#ccc;float:left;margin: 0em 1em;padding:8px;">&nbsp;</div>
<script>
    function getresult(){
        var param = {}
        param["teks"] = $("#teks").val()
        $.post('{{root}}/tag', param, function(data) {
          $("#result").text(data)
        }
        );
        return false;
    }
</script>