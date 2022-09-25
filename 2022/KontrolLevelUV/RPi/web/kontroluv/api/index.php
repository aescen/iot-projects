<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept");
header("Content-Type: application/json; charset=UTF-8");
require __DIR__ . '/vendor/autoload.php'; 

$app = new Slim\App([
    'settings'=>[
        'displayErrorDetails'=>true
    ]
]);

$container = $app->getcontainer();
 
// Register component on container
$container['view'] = function ($container) {
    $view = new \Slim\Views\Twig(__DIR__.'templates', [
        'cache' => false
    ]);

    // Instantiate and add Slim specific extension
    $basePath = rtrim(str_ireplace('index.php', '', $container['request']->getUri()->getBasePath()), '/');
    $view->addExtension(new Slim\Views\TwigExtension($container['router'], $basePath));

    return $view;
};
 
// container untuk DB
$container['db'] = function(){
    require_once '..\db.php';
		$pdo = "mysql:host=" . $servername . ";dbname=" . $dbname;
		return new PDO($pdo, $username, $password);
};

$app->get('/loadlogs',function($request, $response){
    $param    = $request->getParams();
	  $dateSelect    = $param['date'];
    $startTime = $dateSelect . " 00:00:00.000000";
		$endTime = $dateSelect . " 23:59:59.999999";
    $query = "SELECT * FROM `kontroluv_log` WHERE `time_stamp` BETWEEN '$startTime' AND '$endTime' ORDER BY `kontroluv_log`.`time_stamp` DESC";
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    
    return json_encode($mAsset);        
});

$app->run();
?>