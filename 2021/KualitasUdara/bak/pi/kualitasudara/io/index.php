<?php
	header("Access-Control-Allow-Origin: *");
	header("Content-Type: application/json; charset=UTF-8");
	require __DIR__ . '/vendor/autoload.php'; 
	use Slim\Http\Request;
	use Slim\Http\Response;
	use Slim\Http\UploadedFile;

	$app = new Slim\App([
		'settings'=>[
			'displayErrorDetails' => true,
			'addContentLengthHeader' => false
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
		require_once '../db.php';
		$pdo = "mysql:host=" . $servername . ";dbname=" . $dbname;
		return new PDO($pdo, $username, $password);
	};

	$app->get('/loaddata/',function($request,$response){
		$param    = $request->getQueryParams();
		##var_dump($param);
		$id    = $param['id'];
		$query    = "SELECT * FROM `kualitasudara` WHERE `id` = $id;";
		##echo $query;
		$mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		return json_encode($mAsset);        
	});
	
	$app->post('/updatedata',function($request,$response){
		$param    = $request->getParams();
		#var_dump($param);
		$id    = $param['id'];
		$ppm1  = $param['ppm1'];
		$ppm2  = $param['ppm2'];
		$ppm3  = $param['ppm3'];
		$dust  = $param['dust'];
		$jumlah = $param['jumlah'];
		$query1    = "UPDATE `kualitasudara` SET `ppm1` = '$ppm1', `ppm2` = '$ppm2', `ppm3` = '$ppm3', `dust` = '$dust', `jumlah` = '$jumlah' WHERE `kualitasudara`.`id` = $id;";
		#echo $query1;
		$query2	  = "SELECT *  FROM `kualitasudara` WHERE `id` = $id AND `ppm1` LIKE '$ppm1' AND `ppm2` LIKE '$ppm2' AND `ppm3` LIKE '$ppm3' AND `dust` LIKE '$dust' AND `jumlah` LIKE '$jumlah' ORDER BY `id` DESC LIMIT 1;";
		$commit1   = $this->db->query($query1)->fetchAll(PDO::FETCH_ASSOC);
		$mAsset   = $this->db->query($query2)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		if (!empty($mAsset)) {
			$mAsset = array('update' => true);
		}else{
			$mAsset = array('update' => false);
		}
		#echo print_r($mAsset);
		return json_encode($mAsset);        
	});
	
	$app->run();
?>