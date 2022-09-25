<!-- PHP.MySQL.START -->
<?php
	require_once 'inits.php';
	require_once 'db.php';

	$result = $conn->query($sql);
  if ( $result->num_rows > 0 ) {
    while( $row = $result->fetch_assoc() ) {
      $nodeStatus[$row['node_id']] = $row['power_usage'];
      $nodeColor[$row['node_id']] = $row['info'];
      $totalWatt = $totalWatt + $row['power_usage'];
    }
    
    $totalWattColor = getColorForWatt($totalWatt, WATT_TOTAL_BERLEBIH, TOTAL_INFO_COLOR);
  }
?>
<!-- PHP.MySQL.END --> 

<div id="wrapper">
    <div id="container">
        <!------------------------------------------------------------------------------ chart start -->
        <ol class="organizational-chart">
            <li>
                <!---------------------------------------------------------------------- header -->
                <div class="oc-color-<?php echo $totalWattColor; ?>">
                    <h1>Beban Listrik: <span id="total-watt"><?php echo $totalWatt; ?></span>w</h1>
                </div>
                <!---------------------------------------------------------------------- node start -->
                <ol>
                    <!------------------------------------------------------------------ Node A -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['1']]]; ?>">
                            <h2>Node&nbsp;1:</h2>
                            <h3 id="node-1"><?php echo $nodeStatus['1']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi A1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi A2</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi B1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi B2</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi C1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi C2</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node B -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['2']]]; ?>">
                            <h2>Node&nbsp;2:</h2>
                            <h3 id="node-3"><?php echo $nodeStatus['2']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi A3</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi A4</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi B3</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi B4</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi C3</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi C4</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node C -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['3']]]; ?>">
                            <h2>Node&nbsp;3:</h2>
                            <h3 id="node-3"><?php echo $nodeStatus['3']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi D1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi D2</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi F1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi F2</h3>
                                </div>
                            </li><li>
                                <div class="oc-color-grey">
                                    <h3>Toilet</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node D -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['4']]]; ?>">
                            <h2>Node&nbsp;4:</h2>
                            <h3 id="node-4"><?php echo $nodeStatus['4']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi D3</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi D4</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi E1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi E2</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi F3</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kursi F4</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node E -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['5']]]; ?>">
                            <h2>Node&nbsp;5:</h2>
                            <h3 id="node-5"><?php echo $nodeStatus['5']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Dispenser</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node F -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['6']]]; ?>">
                            <h2>Node&nbsp;6:</h2>
                            <h3 id="node-6"><?php echo $nodeStatus['6']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Coffee Maker</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node G -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['7']]]; ?>">
                            <h2>Node&nbsp;7:</h2>
                            <h3 id="node-7"><?php echo $nodeStatus['7']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>Kulkas Mini</h3>
                                </div>
                            </li>
                        </ol>
                    </li>
                    
                    <!------------------------------------------------------------------ Node H -->
                    <li>
                        <div class="oc-color-<?php echo NODE_INFO_COLOR[NODE_INFO[$nodeColor['8']]]; ?>">
                            <h2>Node&nbsp;8:</h2>
                            <h3 id="node-8"><?php echo $nodeStatus['8']; ?>w</h3>
                        </div>
                        <ol>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>TV 1</h3>
                                </div>
                            </li>
                            <li>
                                <div class="oc-color-grey">
                                    <h3>TV 2</h3>
                                </div>
                            </li>
                        </ol>
                    </li>

                <!---------------------------------------------------------------------- node end -->
                </ol>
            </li>
        </ol>
        <!------------------------------------------------------------------------------ chart end -->
    </div>
</div>