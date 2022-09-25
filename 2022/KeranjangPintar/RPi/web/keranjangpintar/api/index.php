<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept");
header("Content-Type: application/json; charset=UTF-8");
require __DIR__ . '/vendor/autoload.php'; 

function isEmpty($value) {
  if(is_scalar($value) === false) throw new InvalidArgumentException('Please only provide scalar data to this function');

  if(is_array($value) === false) return empty(trim($value));

  if(count($value) === 0) return true;

  foreach($value as $val) {
    if(isEmpty($val) === false) return false;
  }

  return false;
}

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

$app->get('/getpos',function($request, $response){
    $param       = $request->getParams();
	  $idKeranjang = $param['idKeranjang'];
    if (intval($idKeranjang) >= 0 ) {
      $sql       = "SELECT
                      `keranjang_user`.`nama` AS nama_user,
                      `keranjang_produk`.`nama` AS nama_produk,
                      `keranjang_produk`.`deskripsi`,
                      `keranjang_produk`.`harga`,
                      `keranjang_produk`.`sisa`,
                      `keranjang_produk`.`img_url`,
                      `keranjang_pos`.*
                    FROM
                      `keranjang_pos`
                    INNER JOIN
                      `keranjang_keranjang`
                     ON
                      `keranjang_keranjang`.`id` = `keranjang_pos`.`id_keranjang`
                    INNER JOIN `keranjang_user`
                     ON
                      `keranjang_user`.`id` = `keranjang_pos`.`id_user`
                    INNER JOIN `keranjang_produk`
                     ON 
                      `keranjang_produk`.`id` = `keranjang_pos`.`id_produk`
                    WHERE `keranjang_keranjang`.`id` = '".$idKeranjang."'";
      $keranjang  = $this->db->query($sql)->fetchAll(PDO::FETCH_ASSOC);
      return json_encode($keranjang);
    }
    return json_encode([]);
});

$app->get('/getkeranjang', function($request, $response){
  $param       = $request->getParams();
  $keranjang   = $param['keranjang'];

  if (isEmpty($keranjang) >= 0) {
    $sql       = "SELECT id FROM `keranjang_keranjang` WHERE `keranjang` = '".$keranjang."'";
    $idKeranjang  = $this->db->query($sql)->fetchAll(PDO::FETCH_ASSOC);
    return json_encode($idKeranjang);
  }

  return json_encode([]);
});

$app->run();
?>
