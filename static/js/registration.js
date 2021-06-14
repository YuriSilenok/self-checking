document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('password1').onkeyup = checkPasswordMatch;
    document.getElementById('password2').onkeyup = checkPasswordMatch;
});
function checkPasswordMatch() {
    if (document.getElementById('password1').value != document.getElementById('password2').value
    || document.getElementById('password1').value == ""
    || document.getElementById('password2').value == ""){
        document.getElementById("btn_reg").disabled = true;
        if (document.getElementById('password1').value != "" && document.getElementById('password2').value != ""){
            document.getElementById("password1").style.backgroundColor = "#ff707e";
            document.getElementById("password2").style.backgroundColor = "#ff707e";
        }
    }else{
        document.getElementById("btn_reg").disabled = false;
        document.getElementById("password1").style.backgroundColor = "#ffffff";
        document.getElementById("password2").style.backgroundColor = "#ffffff";
    }
}