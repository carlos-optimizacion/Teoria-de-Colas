"""Perfil visual compartido para los cinco visores Three.js activos.

No cambia eventos, réplicas ni cálculos. Se incrusta en cada reproductor
para aplicar iluminación coherente, controles de calidad y métricas de render.
"""

QUALITY_JS = r"""
// Calidad adaptable. Auto preserva GPU/memoria en pantallas pequeñas.
function setupVisualQuality(THREE,renderer,scene,stage,profile='indoor'){
  const profiles={
    banco:{sky:0xecf5ff,ground:0x9badbf,key:0xfff0de,fill:0xaedaf1,exposure:1.24},
    hospital:{sky:0xf0ffff,ground:0x93b5ad,key:0xffffff,fill:0x9fe1d4,exposure:1.19},
    supermercado:{sky:0xfff6e6,ground:0xa9a19a,key:0xfff1d3,fill:0xc0e0d6,exposure:1.22},
    logistica:{sky:0xe1f2fe,ground:0x8fa2aa,key:0xfff4df,fill:0xafd6ef,exposure:1.17},
    network:{sky:0xe4f4ff,ground:0x9eb2bf,key:0xfff6e9,fill:0xa7ddf1,exposure:1.20}
  };
  const look=profiles[profile]||profiles.network;
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure=look.exposure;
  renderer.shadowMap.enabled=true;
  renderer.shadowMap.type=THREE.PCFSoftShadowMap;
  const skylight=new THREE.HemisphereLight(look.sky,look.ground,1.70);
  scene.add(skylight);
  const sun=new THREE.DirectionalLight(look.key,2.45);
  sun.position.set(-6,16,9);sun.castShadow=true;
  sun.shadow.camera.left=-18;sun.shadow.camera.right=18;
  sun.shadow.camera.top=18;sun.shadow.camera.bottom=-18;
  sun.shadow.camera.near=.5;sun.shadow.camera.far=58;
  sun.shadow.bias=-.00009;sun.shadow.normalBias=.035;
  sun.shadow.radius=2.25;
  scene.add(sun);
  const fill=new THREE.DirectionalLight(look.fill,.72);
  fill.position.set(9,9,-7);fill.castShadow=false;scene.add(fill);
  const controller={mode:'auto',active:'',pixelRatio:1,shadow:1024};
  const memory=Number(navigator.deviceMemory||0);
  const compact=window.matchMedia('(max-width: 850px)').matches||(memory>0&&memory<=4);
  function apply(mode='auto'){
    if(!['auto','high','balanced','economy'].includes(mode))mode='auto';
    const level=mode==='auto'?(compact?'balanced':'high'):mode;
    const nativeDpr=Math.max(1,window.devicePixelRatio||1);
    // Supermuestreo real en monitores estándar; no solo en pantallas Retina.
    const density=level==='high'?Math.min(nativeDpr*1.45,2.25):
      level==='balanced'?Math.min(nativeDpr,1.5):Math.min(nativeDpr*.75,1);
    const shadowResolution=level==='high'?2048:level==='balanced'?1024:512;
    renderer.setPixelRatio(density);
    if(sun.shadow.mapSize.x!==shadowResolution){
      sun.shadow.mapSize.set(shadowResolution,shadowResolution);
      if(sun.shadow.map)sun.shadow.map.dispose();
      sun.shadow.map=null;
      sun.shadow.needsUpdate=true;
    }
    controller.mode=mode;controller.active=level;
    controller.pixelRatio=density;controller.shadow=shadowResolution;
    stage.dataset.visualQuality=level;
    stage.dataset.qualityMode=mode;
    stage.dataset.renderScale=density.toFixed(2);
    stage.dataset.shadowResolution=String(shadowResolution);
    return controller;
  }
  apply('auto');
  return {apply,controller,sun};
}
"""


def embed_quality(html: str) -> str:
    """Insert the helper into one (and only one) Three.js ES module block."""
    if html.count("/*__QUALITY__*/") != 1:
        raise ValueError("La escena requiere una única ubicación para el perfil visual")
    return html.replace("/*__QUALITY__*/", QUALITY_JS)
