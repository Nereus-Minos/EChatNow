$(function(){

	var error_name = false;
	var error_password = false;



	$('#user_name').blur(function() {
		check_user_name();
	});

	$('#user_name').focus(function() {
		$(this).next().hide();
	});


	$('#pwd').blur(function() {
		check_pwd();
	});

	$('#pwd').focus(function() {
		$(this).next().hide();
	});

	$('#cpwd').blur(function() {
		check_cpwd();
	});

	$('#cpwd').focus(function() {
		$(this).next().hide();
	});

	$('#email').blur(function() {
		check_email();
	});

	$('#email').focus(function() {
		$(this).next().hide();
	});

	$('#allow').click(function() {
		if($(this).is(':checked'))
		{
			error_check = false;
			$(this).siblings('span').hide();
		}
		else
		{
			error_check = true;
			$(this).siblings('span').html('请勾选同意');
			$(this).siblings('span').show();
		}
	});


	function check_user_name(){
		//数字字母或下划线
		var reg = /^\w{6,15}$/;
		var val = $('#user_name').val();

		if(val==''){
			$('#user_name').next().html('用户名不能为空！')
			$('#user_name').next().show();
			error_name = true;
			return;
		}

		if(reg.test(val))
		{
			$('#user_name').next().hide();
			error_name = false;
		}
		else
		{
			$('#user_name').next().html('用户名是5到15个英文或数字，还可包含“_”')
			$('#user_name').next().show();
			error_name = true;
		}

	}


	function check_pwd(){
		var reg = /^[\w@!#$%&^*]{6,15}$/;
		var val = $('#pwd').val();

		if(val==''){
			$('#pwd').next().html('密码不能为空！')
			$('#pwd').next().show();
			error_password = true;
			return;
		}

		if(reg.test(val))
		{
			$('#pwd').next().hide();
			error_password = false;
		}
		else
		{
			$('#pwd').next().html('密码是6到15位字母、数字，还可包含@!#$%^&*字符')
			$('#pwd').next().show();
			error_password = true;
		}		
	}




	$('.reg_form').submit(function() {

		check_user_name();
		check_pwd();
		check_cpwd();
		check_email();

		if(error_name == false && error_password == false )
		{
			return true;
		}
		else
		{
			return false;
		}

	});








})