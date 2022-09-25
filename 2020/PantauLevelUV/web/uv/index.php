<?php
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
    return new PDO('mysql:host=localhost;dbname=pi','pi','raspberry');
};

$app->post('/loaddata.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel ORDER BY `id`";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->post('/loadfan.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel WHERE `id`='fan'";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->post('/loadhumidity.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel WHERE `id`='humidity'";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->post('/loadlamp.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel WHERE `id`='lamp'";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->post('/loadtemperature.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel WHERE `id`='temperature'";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->post('/loaduvlevel.php',function($request,$response){
    $param    = $request->getParams();    
	$tabel    = $param['tabel'];
    $mReturn  = array();
    $query    = "SELECT * FROM $tabel WHERE `id`='uvLevel'";  
    $mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);    

    return json_encode($mAsset);        
});

$app->run();
?>