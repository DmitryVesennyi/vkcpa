Кнопка авторизации:

	<a href="https://oauth.vk.com/authorize?client_id=5818381&display=page&redirect_uri=http://kitona.ru/go-in&scope=friends,wall,photos,video,offline,groups,stats&response_type=code&v=5.60">
		<button class="btn btn-sm btn-info">ВХОД</button>
	</a>
	
// http://kitona.ru/go-in - го-ин - адрес странички со скриптом обработки ответа от ВК
// scope - права доступа. Нам нужен минимум ('offline' - это получение бессрочного токена)

// Сам скрипт обработки ответа от вк

// получаем в ГЕТ ответ по нажатию кнопки
	$code			= $_GET['code'];
	
	$client_id		= 'ИД приложения';	
	$client_secret	= 'СекретКей приложения';
	$redirect_uri	= 'http://kitona.ru/go-in'; // адрес скрипта обработки ответа
	
// обращаемся к АПИ ВК для получения токена используя code
if (isset($code)) { // если есть code...
	$gettoken = 'https://oauth.vk.com/access_token?client_id='.$client_id.'&client_secret='.$client_secret.'&redirect_uri='.$redirect_uri.'&code='.$code;

// переходим по ссылке с запросом для получения токена
	$result			= json_decode(file_get_contents($gettoken));

	$token			= $result -> access_token;
	$userid			= $result -> user_id;
}else{
// если code пустой кидаем на главную
	$app->redirect(JRoute::_(JURI::root())); // (дела джумлы, не чистый php)
}

// если token не пустой запускаем регистрацию или авторизацию

if (isset($token)) {
	
// обращаемся к VK для получения данных пользователя
	$s = file_get_contents('https://api.vk.com/method/users.get?user_ids='.$userid.'&fields=photo_100&name_case=Nom&lang=ru&v=5.52');

	$userVK			= json_decode($s);

	$usName		= $userVK -> response[0]->first_name.' '.$userVK -> response[0]->last_name;
	$uId				= $userVK -> response[0]->id;
	$photo			= $userVK -> response[0]->photo_100;
	$photolink		= '<img src="'.$photo.'" />';

// проверяем есть ли юзер с таким ид в базе	
	$user_id		= JUserHelper::getUserId($uId); // (дела джумлы, не чистый php)
	$session			= JFactory::getSession(); // (Получаем объект сессии - дела джумлы)
	$session->set('vktoken', $token); // заносим токен в сессию
	$session->set('vkphoto', $photo); // заносим аву в сессию

// если пользователя нет в базе регистрируем нового (дела джумлы, не чистый php)
	if (!$user_id) {
	$pass	= JUserHelper::getCryptedPassword(JUserHelper::genRandomPassword());
	$user = new JUser;
	$userData = array( 
		'name'			=> $usName,
		'username'		=> $uId,
		'password'		=> $pass,
		'password2'		=> $pass,
		'email'			=>$uId.'@vk.com',
		'groups'			=> array( 2 )
	);
	
// подключаем плагин юзера джумлы
 	JPluginHelper::importPlugin('user');
	$user->bind( $userData );
	if ( $user->save() ) {
		
		$instance			= JUser::getInstance($user->id);
		$session				= JFactory::getSession();
		$instance->guest	= 0;
		$instance->aid	= 1;
		$session->set('user', $instance);		

//		echo 'Пользователь ' . $user->username . ' успешно зарегестрирован!<br>'; // дебаг
	}
// если пользователь есть, авторизуем (дела джумлы)
	}else{
	 	JPluginHelper::importPlugin('user');
		$instance			= JUser::getInstance($user_id);
		$session				= JFactory::getSession();
		$instance->guest	= 0;
		$instance->aid	= 1;
		$session->set('user', $instance);
		
// обновляем таблицу сессии		
	$app->checkSession();
	$db = JFactory::getDBO();
	$db->setQuery(
		'UPDATE '.$db->quoteName('#__session').
		' SET '.$db->quoteName('guest').' = '.$db->quote($instance->get('guest')).',' .
		'	'.$db->quoteName('username').' = '.$db->quote($instance->get('username')).',' .
		'	'.$db->quoteName('userid').' = '.(int) $instance->get('id').
		' WHERE '.$db->quoteName('session_id').' = '.$db->quote($session->getId())
	);
	$db->query();

// это ава, не важно (пишем в базу)
if($photo!=''){
	$db = JFactory::getDBO();
	$q = "UPDATE `#__users` SET `vkphoto` = '$photo' WHERE `username` = '$uId'";
	$db->setQuery($q);
	$db->query();
}	
	
// пишем в базу дату последнего визита (дела джумлы)
		$instance->setLastVisit();
	}

// после успеха кидаем на главную
	$app->redirect(JRoute::_(JURI::root()));
}else{
// если токена нет кидаем на главную
	$app->redirect(JRoute::_(JURI::root()));
}
    parent::display($tpl);//  (дела джумлы с передачей инфы в шаблон)
  }
}