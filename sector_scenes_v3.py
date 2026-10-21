"""Objetos y arquitectura ambiental por sector, sin lógica de colas.

Se incrusta como JavaScript sin dependencias adicionales. Los escenarios comparten
solo contrato de eventos, cámaras e indicadores; no comparten mobiliario.
"""

ENVIRONMENT_JS = r"""
  const palettes={
    banco:[0xe8eff1,0xf8f8f1,0x194966,0xd6ad65],
    hospital:[0xe8f4ef,0xf7fffc,0x2c8686,0x7fc6b8],
    supermercado:[0xf2eadb,0xfffbf0,0x277951,0xe6b84e],
    logistica:[0xa8b4b8,0x6b8795,0x274859,0xf0bf4b],
    fabrica:[0xd1dadc,0xe9eef0,0x3b5262,0xe5a65c]
  };
  const colors=palettes[sector],ground=mat(colors[0]),wall=mat(colors[1]),
        accent=mat(colors[2]),highlight=mat(colors[3]);
  const features={seats:0,racks:0,triage:0,forklift:0,docks:0,checkoutDecor:0};
  const sign=(words,x,y,z,w=3.0,h=.45,ink=0x154e70)=>{
    const item=label(words,w,h,ink,47);item.position.set(x,y,z);scene.add(item);return item;
  };
  const chair=(x,z,color=blue)=>{
    box(.72,.12,.64,color,[x,.47,z]);
    box(.72,.74,.11,color,[x,.85,z-.26]);
    for(const side of [-1,1])cyl(.045,.045,.43,steel,[x+side*.3,.22,z+.2]);
    features.seats++;
  };
  const plant=(x,z)=>{
    cyl(.32,.27,.48,wood,[x,.24,z]);
    cyl(.07,.08,.88,mat(0x426751),[x,.88,z]);
    for(let i=0;i<5;i++){
      const leaf=sphere(.26,mat(0x52a37c),[x+Math.sin(i*2.1)*.22,1.2+Math.cos(i*3)*.08,z+Math.cos(i*2.1)*.16]);
      leaf.scale.set(.8,1.2,.8);
    }
  };
  const paint=(x,z,w,d,m)=>box(w,.011,d,m,[x,-.019,z]);
  box(23,.25,20,ground,[0,-.17,0]);
  box(23,3.7,.27,wall,[0,1.75,-9.8]);
  if(sector==='logistica'){
    // PATIO LOGÍSTICO: muelles, vialidad, racks, montacargas y puertas de carga.
    box(23,.30,.80,accent,[0,3.80,-9.45]);
    box(23,.11,.78,highlight,[0,3.44,-9.36]);
    box(23,.16,3.5,mat(0x607d8c),[0,3.86,-7.85]);
    for(let x=-10;x<=10;x+=5.0)box(.16,3.55,.16,steel,[x,1.73,-7.85]);
    box(10,.75,.08,accent,[0,2.95,-9.54]);
    sign('CENTRO DE DISTRIBUCIÓN',0,2.98,-9.42,8.7,.54,0xffffff);
    for(const side of [-1,1]){
      for(let z=-8;z<=8;z+=2)box(.12,1.40,.12,steel,[side*11.4,.7,z]);
      box(.09,.10,19,steel,[side*11.4,1.39,0]);
      for(let z=-7;z<=8;z+=2.0)paint(side*9.4,z,.10,1.02,highlight);
    }
    for(const x of [-4.7,4.7])for(let z=1;z<=8;z+=2)paint(x,z,.10,1.1,highlight);
    for(let z=1.9;z<=8.0;z+=2.0)paint(0,z,1.55,.10,mat(0xf6f3e9));
    // Carga paletizada en las laterales, fuera del espacio de circulación.
    for(const x of [-9.25,9.25])for(let j=0;j<3;j++){
      const z=-3+j*1.12;
      box(1.25,.13,.93,wood,[x,.08,z]);
      box(.90,.51,.75,mat(j%2?0xb68d5e:0xcda471),[x,.41,z]);
      box(.90,.51,.75,mat(0xc49a65),[x,.94,z]);
    }
    const fork=new THREE.Group();fork.position.set(-9.1,0,-5.7);scene.add(fork);
    box(1.05,.76,1.16,highlight,[0,.55,0],fork);
    box(.73,.53,.78,accent,[0,1.22,.02],fork);
    for(const x of [-.56,.56])for(const z of [-.38,.43]){
      const tire=cyl(.22,.22,.13,mat(0x283139),[x,.20,z],fork);
      tire.rotation.z=Math.PI/2;
    }
    for(const x of [-.41,.41]){
      box(.12,2.05,.13,steel,[x,1.05,.96],fork);
      box(.12,.11,1.13,steel,[x,.16,1.46],fork);
    }
    features.forklift=1;
    sign('INGRESO DE CAMIONES',-7.5,2.47,9.53,3.15,.41,0x135f80);
    sign('SALIDA DE DESPACHOS',7.5,2.47,9.53,3.25,.41,0x1b7855);
  } else {
    // Recinto cerrado solamente en escenarios con atención de personas.
    box(.24,3.7,20,wall,[-11.4,1.75,0]);
    box(.24,3.7,20,wall,[11.4,1.75,0]);
    box(23,.25,.35,accent,[0,3.62,-9.62]);
    box(23,.11,.35,highlight,[0,3.41,-9.56]);
    box(9.3,.92,.08,accent,[0,2.76,-9.53]);
    sign(sceneDef.title+' · DECISION LAB',0,2.78,-9.43,8.5,.65,0xffffff);
    const grout=mat(sector==='supermercado'?0xd7cbba:sector==='hospital'?0xc7e1d8:0xc5d8e1);
    for(let x=-10.5;x<=10.5;x+=1.5)box(.024,.004,19.5,grout,[x,-.005,0]);
    for(let z=-9;z<=9;z+=1.5)box(22,.004,.024,grout,[0,-.005,z]);
    for(const x of [-10,-8.4,-6.8,6.8,8.4,10])box(.052,2.8,.07,steel,[x,1.5,9.65]);
    for(const x of [-7.6,7.6])box(4,.09,.07,steel,[x,2.95,9.65]);
    sign(sceneDef.entry,-7.4,2.45,9.47,2.4,.43,0x0d6889);
    sign(sceneDef.finish,7.5,2.45,9.47,2.5,.43,0x198467);
    if(sector==='banco'){
      // Agente de seguridad, recepción, turnero y butacas de espera.
      box(.95,1.43,.55,accent,[-8,.72,6.35]);
      box(.90,.14,.54,blue,[-8,1.49,6.35]);
      sign('TURNOS',-8,1.23,6.66,.83,.23,0xffffff);
      for(const x of [-8.7,-7.5,-6.3])chair(x,1.8);
      plant(-10,-7.65);plant(10,-7.65);
      box(3.5,.97,.59,wood,[8.45,.48,4.6]);
      box(3.53,.11,.73,accent,[8.45,1.02,4.6]);
      sign('INFORMES',8.5,1.5,4.94,2.35,.33,0x164c68);
    } else if(sector==='hospital'){
      // Puesto de triaje, banco de pacientes y corredor asistencial.
      box(3.05,.96,.77,mat(0x80b8ae),[-8.8,.49,5.55]);
      box(3.14,.12,.92,accent,[-8.8,1.00,5.55]);
      sign('TRIAJE',-8.8,1.52,5.97,1.5,.32,0xffffff);
      features.triage=1;
      for(const z of [1.5,3.0])for(const x of [-9.6,-8.55,-7.5])
        chair(x,z,mat(0x7db6ba));
      box(.87,1.32,.56,mat(0xe1f4ef),[-8.4,.66,7.35]);
      sign('ADMISIÓN',-8.4,1.49,7.67,1.30,.25,0x127b72);
      sign('✚ URGENCIAS',0,1.58,-9.43,3.4,.42,0xffffff);
      for(let z=-6;z<8;z+=2.7)paint(0,z,.06,1.1,mat(0x70b9b0));
      // Botiquines en pared junto al pasillo asistencial.
      for(const x of [-9.95,9.95]){
        box(.78,.65,.22,mat(0xffffff),[x,1.86,-6.7]);
        sign('✚',x,1.86,-6.53,.47,.35,0xc84f59);
      }
    } else if(sector==='supermercado'){
      // Góndolas con mercancía real, cajas centrales, frutas y cestas.
      const shelf=(x,z)=>{
        for(const h of [.42,1.00,1.58]){
          box(1.55,.11,1.50,steel,[x,h,z]);
          for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){
            const pigment=[0xd6a754,0x65b395,0xc97168,0x7797b8][(a+b+8)%4];
            box(.29,.26,.33,mat(pigment),[x+a*.46,h+.19,z+b*.47]);
          }
        }
        for(const dx of [-.74,.74])box(.06,2,.08,accent,[x+dx,1,z-.62]);
        features.racks++;
      };
      for(const x of [-9.15,9.15])for(const z of [-2.8,-.2,2.4])shelf(x,z);
      box(3.0,.16,1.55,wood,[-8.9,.57,5.65]);
      for(const x of [-9.95,-9.25,-8.55,-7.85])
        sphere(.34,mat(x<-9?0x9dbf67:0xc97452),[x,.83,5.65]);
      sign('FRUTAS FRESCAS',-8.85,1.55,5.97,2.9,.34,0x216c4b);
      for(const x of [7.8,8.85,9.9])box(.81,.58,.69,mat(0x3d906d),[x,.30,5.8]);
      sign('PROMOCIONES',8.8,2.48,6.13,2.6,.41,0x1c8052);
      features.checkoutDecor=1;
    }
  }
  if(sector==='banco'){
    for(const x of [-3.55,3.55]){
      for(const z of [2,4,6]){
        cyl(.07,.07,1.0,steel,[x,.5,z]);
        sphere(.11,highlight,[x,1.02,z]);
      }
      const rope=cyl(.035,.035,4,blue,[x,.88,4]);rope.rotation.x=Math.PI/2;
    }
  }
  if(sector==='supermercado')for(const x of [-5.6,5.6])
    paint(x,4,.10,4.7,highlight);
  const floorLabel=label(sceneDef.floor,4.1,.43,
                         sector==='logistica'?0xfff0bb:0x427c9a,40);
  floorLabel.rotation.x=-Math.PI/2;floorLabel.position.set(0,.025,7.62);scene.add(floorLabel);
  stage.dataset.features=JSON.stringify(features);
"""
