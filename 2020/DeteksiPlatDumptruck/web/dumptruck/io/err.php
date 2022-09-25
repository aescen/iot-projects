<html><head><meta http-equiv='Content-Type' content='text/html; charset=utf-8'><title>Slim Application Error</title><style>body{margin:0;padding:30px;font:12px/1.5 Helvetica,Arial,Verdana,sans-serif;}h1{margin:0;font-size:48px;font-weight:normal;line-height:48px;}strong{display:inline-block;width:65px;}</style></head><body><h1>Slim Application Error</h1><p>The application could not run because of the following error:</p><h2>Details</h2><div><strong>Type:</strong> RuntimeException</div><div><strong>Message:</strong> Error moving uploaded file 4.10. Threshold resized.png to ../imgs\</div><div><strong>File:</strong> C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Http\UploadedFile.php</div><div><strong>Line:</strong> 247</div><h2>Trace</h2><pre>#0 C:\xampp\htdocs\dumptruck-jtd\io\index.php(95): Slim\Http\UploadedFile-&gt;moveTo('../imgs\\')
#1 C:\xampp\htdocs\dumptruck-jtd\io\index.php(82): moveUploadedFile('../imgs', Object(Slim\Http\UploadedFile), NULL)
#2 [internal function]: Closure-&gt;{closure}(Object(Slim\Http\Request), Object(Slim\Http\Response), Array)
#3 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Handlers\Strategies\RequestResponse.php(41): call_user_func(Object(Closure), Object(Slim\Http\Request), Object(Slim\Http\Response), Array)
#4 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Route.php(335): Slim\Handlers\Strategies\RequestResponse-&gt;__invoke(Object(Closure), Object(Slim\Http\Request), Object(Slim\Http\Response), Array)
#5 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\MiddlewareAwareTrait.php(117): Slim\Route-&gt;__invoke(Object(Slim\Http\Request), Object(Slim\Http\Response))
#6 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Route.php(313): Slim\Route-&gt;callMiddlewareStack(Object(Slim\Http\Request), Object(Slim\Http\Response))
#7 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\App.php(495): Slim\Route-&gt;run(Object(Slim\Http\Request), Object(Slim\Http\Response))
#8 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\MiddlewareAwareTrait.php(117): Slim\App-&gt;__invoke(Object(Slim\Http\Request), Object(Slim\Http\Response))
#9 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\App.php(388): Slim\App-&gt;callMiddlewareStack(Object(Slim\Http\Request), Object(Slim\Http\Response))
#10 C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\App.php(296): Slim\App-&gt;process(Object(Slim\Http\Request), Object(Slim\Http\Response))
#11 C:\xampp\htdocs\dumptruck-jtd\io\index.php(99): Slim\App-&gt;run()
#12 {main}</pre></body></html><br />
<b>Warning</b>:  move_uploaded_file(): The second argument to copy() function cannot be a directory in <b>C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Http\UploadedFile.php</b> on line <b>246</b><br />
<br />
<b>Warning</b>:  move_uploaded_file(): Unable to move 'C:\xampp\tmp\phpDC14.tmp' to '../imgs\' in <b>C:\xampp\htdocs\dumptruck-jtd\io\vendor\slim\slim\Slim\Http\UploadedFile.php</b> on line <b>246</b><br />
