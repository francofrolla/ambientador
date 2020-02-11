  lista = []

  for x in range(0,len(nombres)):
    estado = arrayfechas[x].value
    if estado == True:
      nombre = idsatelite[x]
      lista.append(nombre)

  tamaño = len(lista)

  ##GRAFICAMOS POR SEPARADO !! ZARPADAL
  limites = lote.centroid()
  centro = limites.getInfo()
  centro = centro['coordinates']
  centro_array = [centro[1],centro[0]]

  #GRAFICAMOS IMAGENES DE INTERES EN UN MAPA
  # Import the Folium library.
  import folium
  import ipywidgets as widgets
  from IPython.display import display
  from ipywidgets import Checkbox
  import branca.colormap as cm
  palette = ['#FFFFFF', '#CE7E45', '#DF923D', '#F1B555', '#FCD163', '#99B718', '#74A901', '#66A000', '#529400', '#3E8601', '#207401', '#056201', '#004C00', '#023B01', '#012E01', '#011D01', '#011301']


  # Define a method for displaying Earth Engine image tiles to folium map.
  def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
      tiles = map_id_dict['tile_fetcher'].url_format,
      #tiles = "Stamen Terrain",
      attr = 'Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name = name,
      overlay = True,
      control = True
    ).add_to(self)

  # Add EE drawing method to folium.
  folium.Map.add_ee_layer = add_ee_layer


  # Create a folium map object.


  for x in range(0,tamaño):
    my_map = folium.Map(location=centro_array, zoom_start=14,width='60%',height='60%')

    laimagen = ee.Image(lista[x])
    id_imagen = laimagen.id().getInfo()
    escena = laimagen.clip(lote)
    escena = escena.normalizedDifference(['B8', 'B4']).rename('NDVI')
    escena = escena.select(["NDVI"])
    escenacompleta = laimagen.clip(lote.buffer(2000))

    params = escenacompleta.select(["B4","B3","B2"]).reduceRegion(
      reducer= ee.Reducer.percentile([5, 95]), 
      geometry= lote.buffer(1000), 
      scale= 10,
      )
    parametros = params.getInfo()
    min_escena = [parametros['B4_p5'], parametros['B3_p5'], parametros['B2_p5']]
    max_escena = [parametros['B4_p95'], parametros['B3_p95'], parametros['B2_p95']]

    params = escena.reduceRegion(
      reducer= ee.Reducer.percentile([10, 90]), 
      geometry= lote, 
      scale= 10,
      )

    parametros = params.getInfo()
    min_valor = [parametros['NDVI_p10']]
    max_valor = [parametros['NDVI_p90']]

    vis_params = {
      'min': min_valor,
      'max': max_valor,
      'palette': ['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']}
    visParams = {
      'bands':['B4', 'B3', 'B2'],
      'min': min_escena,
      'max': max_escena,
      }
    colormap = cm.LinearColormap(colors=palette,vmin=min_valor[0],vmax=max_valor[0])
    colormap.add_to(my_map)

    my_map.add_ee_layer(escenacompleta, visParams, id_imagen)                      
    my_map.add_ee_layer(escena, vis_params, "NDVI")
    my_map.add_child(folium.LayerControl())
    print(x)
    display(my_map)
