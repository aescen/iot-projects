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
	$container['upload_directory'] = '../imgs';
	 
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

	$app->post('/loaddata',function($request,$response){
		$param    = $request->getParams();
		##var_dump($param);
		$tabel    = $param['tabel'];
		$query    = "SELECT * FROM $tabel";
		##echo $query;
		$mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		return json_encode($mAsset);        
	});
	
	$app->post('/updatedata',function($request,$response){
		$param    = $request->getParams();
		#var_dump($param);
		$plateNumber    = $param['plateNumber'];
		$comeOut    = $param['comeOut'];
		$dateNow    = $param['dateNow'];
		$query1    = "UPDATE `platenumbershistory` SET `comeOut` = '$comeOut' WHERE `platenumbershistory`.`plateNumbers` LIKE '$plateNumber' AND DATE(comeIn) = '$dateNow' AND comeOut IS NULL;";
		#echo $query1;
		$query2	  = "SELECT * FROM platenumbershistory WHERE `platenumbershistory`.`plateNumbers` LIKE '$plateNumber' AND DATE(comeIn) = '$dateNow' AND DATE(comeOut) = DATE('$comeOut') ORDER BY `ids` DESC LIMIT 1;";
		$commit1   = $this->db->query($query1)->fetchAll(PDO::FETCH_ASSOC);
		$mAsset   = $this->db->query($query2)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		if (!empty($mAsset)) {
			$mAsset = array('update'=>'1');
		}else{
			$mAsset = array('update'=>'0');
		}
		#echo print_r($mAsset);
		return json_encode($mAsset);        
	});
	
	$app->post('/insertdata',function($request,$response){
		$param    = $request->getParams();
		#var_dump($param);
		$plateNumber    = $param['plateNumber'];
		$comeIn   		= $param['comeIn'];
		$query1          = "INSERT INTO `platenumbershistory` (`ids`, `plateNumbers`, `comeIn`, `comeOut`) VALUES (NULL, '$plateNumber', '$comeIn', NULL);";
		#echo $query1;
		$query2	  = "SELECT * FROM `platenumbershistory` WHERE `plateNumbers` LIKE '$plateNumber' AND DATE(comeIn) = DATE('$comeIn') AND comeOut IS NULL;";
		$commit1   = $this->db->exec($query1);
		$mAsset   = $this->db->query($query2)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		if (!empty($mAsset)) {
			$mAsset = array('insert'=>'1');
		}else{
			$mAsset = array('insert'=>'0');
		}
		#echo print_r($mAsset);
		return json_encode($mAsset);
	});
	
	$app->post('/checkdata',function($request,$response){
		$param    = $request->getParams();
		#var_dump($param);
		$plateNumber    = $param['plateNumber'];
		$query    = "SELECT * FROM `platenumbers` WHERE `plateNumbers` LIKE '$plateNumber';";
		#echo $query;
		$mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		if (!empty($mAsset)) {
			$mAsset = array('check'=>'1');
		}else{
			$mAsset = array('check'=>'0');
		}
		#echo print_r($mAsset);
		return json_encode($mAsset);    
	});
	
	$app->post('/checkhistory',function($request,$response){
		$param    = $request->getParams();
		#var_dump($param);
		$plateNumber    = $param['plateNumber'];
		$dateNow    = $param['dateNow'];
		$query    = "SELECT * FROM `platenumbershistory` WHERE `plateNumbers` LIKE '$plateNumber' AND DATE(comeIn) = '$dateNow' AND comeOut IS NULL;";
		#echo $query;
		$mAsset   = $this->db->query($query)->fetchAll(PDO::FETCH_ASSOC);
		#echo print_r($mAsset);
		if (!empty($mAsset)) {
			$mAsset1 = array('history'=>'1');
			$mAsset2 = array('comeIn'=>$mAsset[0]['comeIn']);
			$mAsset = array_merge($mAsset1, $mAsset2);
		}else{
			$mAsset = array('history'=>'0');
		}
		#echo print_r($mAsset);
		return json_encode($mAsset);    
	});
	
	$app->post('/uploadfile', function(Request $request, Response $response) {
		$directory = $this->get('upload_directory');
		$uploadedFiles = $request->getUploadedFiles();
		#var_dump($uploadedFiles);
		
		// handle single input with single file upload
		$uploadedFile = $uploadedFiles['imgfile'];
		$filename = $uploadedFile->getClientFilename();
		if ($uploadedFile->getError() === UPLOAD_ERR_OK) {
			$filename = moveUploadedFile($directory, $uploadedFile, $filename);
			$response->write(json_encode(array("uploaded"=>$filename)));
		}
	});
	
	function moveUploadedFile($directory, UploadedFile $uploadedFile, $filename = 'null')
	{	$extension = pathinfo($uploadedFile->getClientFilename(), PATHINFO_EXTENSION);
		$basename = bin2hex(random_bytes(8)); // see http://php.net/manual/en/function.random-bytes.php
		if($filename == 'null'){
			$filename = sprintf('%s.%0.8s', $basename, $extension);
		}
		$uploadedFile->moveTo($directory . DIRECTORY_SEPARATOR . $filename);
		return $filename;
	}
	
	$app->run();
?>