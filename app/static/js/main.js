var $stage_DOM_elements;
function load_session(session_name){
  console.log("load_session() called");
  $.get("/get_session/"+session_name, function( data ){
          console.log("get request success");
          session_data = data;
          var latitudes = [];
          var longitudes = [];

          stage_to_colors = {};
          var first_loc;

          for (var stage in session_data.locations){
            console.log("stage is " + stage);
            for (l in session_data.locations[stage]){
              var lat = session_data.locations[stage][l]['latitude']
              var lon = session_data.locations[stage][l]['longitude']

              if (first_loc == undefined){
                first_loc = [lat, lon];
              }
              latitudes.push(lat)
              longitudes.push(lon)
              if (!(stage in stage_to_colors)){
                stage_to_colors[stage] = colors[Object.keys(stage_to_colors).length]
              }

              markers.addLayer(L.circle([lat, lon], 1, {
                  color: stage_to_colors[stage],
                  fillColor: stage_to_colors[stage],
                  fillOpacity: 0.5,
                  riseOnHover: true,
                  title: "Stage : " + stage
              }).bindPopup("Stage : "+stage));
            }
          }
          var last_loc = [lat, lon];

          start_marker = L.marker(first_loc).bindPopup("Start").openPopup();
          end_marker = L.marker(last_loc).bindPopup("End").openPopup();
          markers.addLayer(start_marker);
          markers.addLayer(end_marker);

          // find central lat/lon
          var sum_lat = 0;
          var sum_lon = 0;
          for (var i =0; i < latitudes.length; i++){
            sum_lat += latitudes[i];
            sum_lon += longitudes[i];
          }
          center_lat = sum_lat / latitudes.length;
          center_lon = sum_lon / longitudes.length;

          var min_lat = Math.min.apply(null, latitudes);
          var max_lat = Math.max.apply(null, latitudes);
          var min_lon = Math.min.apply(null,longitudes);
          var max_lon = Math.max.apply(null, longitudes);
          console.log("min_lat==" + min_lat);
          console.log("max_lat==" + max_lat);
          console.log("min_lon==" + min_lon);
          console.log("max_lon==" + max_lon);
          var llBounds = L.latLngBounds(L.latLng(min_lat, min_lon),
                                        L.latLng(max_lat, max_lon));
          map.fitBounds(llBounds);
          map.addLayer(markers);

          // add stages to DOM
          load_stages();

        });
}

function load_stages(){
  for (i in $stage_DOM_elements){
    $stage_DOM_elements[i].remove();
  }
  $stage_DOM_elements = [];
  stage_num = 0;
  if($('#choose_stage').length == 0){
    $("stage_box").html('<h1>Choose a stage</h1>');
  }

  for (s in stage_to_colors){
    stage = decodeURIComponent(s);

    var $stage_select = $("<div/>", {
                            id: stage_num+"_div",
                            class: "section stage",
                            html: "<p>"+stage_num + " : "+ stage +"</p>"
                          })

    console.log($stage_select);
    $stage_DOM_elements.push($stage_select);
    $("#stage_box").append($stage_select);
    $("#"+stage_num+"_div").css("background-color", stage_to_colors[s]);
    $("#"+stage_num+"_div").click(function(){

      //add black border
      $( this ).css({"border-style" : "solid",
                     "border-color" : "#000000",
                     "border-width" : "3px"})

      // add interaction_box
      $("#nav").append('<div class="section" id="interaction_box"><h3>Choose an algorithm</h3></div>');
      var $loop_button = $("<button/>",{
                              id: "loop_button",
                              class: "interaction_button",
                          });
      $("#interaction_box").append($loop_button);
    })

    /**
    FINISH ADDING LOOP BUTTON FUNCTIONALITY HERE
    */

    stage_num++;
  }

  $("#nav").add('<div class="section" id="interaction_box"></div>');
  var $loop_button = $("<button/>",{
                          id: "loop_button",
                          class: "interaction_button",
                      });
}
