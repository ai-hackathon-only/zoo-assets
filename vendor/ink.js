// Sumi-e ink look, live. Rebuilds the Freestyle brush lines from a depth and a normal pass.
// Spec: docs/sumi-e/README.md (numbers) and Decision: sumi-e look (#114).
// Use: const ink = new InkLook(THREE, renderer); ink.enabled = true; ink.render(scene, camera);
export class InkLook {
  constructor(THREE, renderer) {
    this.T = THREE; this.renderer = renderer; this.enabled = false; this.lineScale = 1; // thinner lines for wide scenes (park)
    const T = THREE;
    this.depthTex = new T.DepthTexture(1, 1);
    this.depthTex.type = T.UnsignedIntType;
    this.colorRT = new T.WebGLRenderTarget(1, 1, { depthTexture: this.depthTex, samples: 0 });
    this.normalRT = new T.WebGLRenderTarget(1, 1);
    this.normalMat = new T.MeshNormalMaterial();
    this.quadCam = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.mat = new T.ShaderMaterial({
      depthTest: false, depthWrite: false,
      uniforms: {
        tColor: { value: this.colorRT.texture }, tDepth: { value: this.depthTex }, tNormal: { value: this.normalRT.texture },
        res: { value: new T.Vector2(1, 1) }, near: { value: 0.1 }, far: { value: 100 }, k: { value: 1 },
      },
      vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
      fragmentShader: `
        precision highp float;
        varying vec2 vUv;
        uniform sampler2D tColor, tDepth, tNormal;
        uniform vec2 res; uniform float near, far, k;
        float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
        float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
          return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
        float lin(vec2 uv){ float d = texture2D(tDepth, uv).x; float z = d*2.-1.;
          return 2.*near*far / (far + near - z*(far - near)); }
        vec3 ramp(float v){
          vec3 a = vec3(.12,.12,.13), b = vec3(.5), c = vec3(.80,.79,.76), d = vec3(.95,.93,.88);
          if (v < .12) return mix(a, b, smoothstep(0., .12, v));
          if (v < .40) return mix(b, c, smoothstep(.12, .40, v));
          return mix(c, d, smoothstep(.40, .70, v));
        }
        void main(){
          vec2 px = 1. / res;
          float d0 = lin(vUv);
          bool bg = texture2D(tDepth, vUv).x >= .9999;
          vec3 paper = vec3(.93,.89,.80);
          paper *= .97 + .05 * vnoise(vUv * res / 3.) + .02 * vnoise(vUv * res * vec2(.6, .02));
          // wash from the lit colour's luminance
          vec3 col = texture2D(tColor, vUv).rgb;
          float lum = dot(col, vec3(.2126, .7152, .0722));
          float v = clamp(pow(clamp(lum, 0., 1.), .7), 0., 1.);
          vec3 wash = bg ? paper : ramp(v) * (paper / vec3(.93,.89,.80));
          // brush lines: width wobbles, scaled by screen height (5.5 px at 320)
          float wob = 1. + .48 * (vnoise(vUv * 25. * vec2(res.x / res.y, 1.)) * 2. - 1.);
          float wS = 5.5 * k * wob * .5, wC = 1.6 * k * .5;
          float sil = 0., cre = 0.;
          vec2 dirs[4]; dirs[0] = vec2(1,0); dirs[1] = vec2(-1,0); dirs[2] = vec2(0,1); dirs[3] = vec2(0,-1);
          vec3 n0 = texture2D(tNormal, vUv).xyz * 2. - 1.;
          for (int i = 0; i < 4; i++) {
            vec2 o = dirs[i] * px;
            vec2 us = vUv + o * wS, uc = vUv + o * wC;
            bool bgS = texture2D(tDepth, us).x >= .9999;
            float ds = lin(us);
            if (bgS != bg) sil = max(sil, 1.);
            else if (!bg && abs(ds - d0) > .06 * d0 + .02) sil = max(sil, 1.);
            if (!bg) {
              vec3 nc = texture2D(tNormal, uc).xyz * 2. - 1.;
              if (dot(nc, n0) < .77 && abs(lin(uc) - d0) < .05 * d0) cre = max(cre, 1.);
            }
          }
          // keep the thin line sharp: silhouette only counts inside its own half-width on the object side
          vec3 outc = wash;
          outc = mix(outc, vec3(.1), cre * .85);
          outc = mix(outc, vec3(.03), sil);
          gl_FragColor = vec4(outc, 1.);
        }`,
    });
    this.quad = new T.Mesh(new T.PlaneGeometry(2, 2), this.mat);
    this.quadScene = new T.Scene(); this.quadScene.add(this.quad);
    this.quad.frustumCulled = false;
  }
  render(scene, camera) {
    const r = this.renderer;
    if (!this.enabled) { r.render(scene, camera); return; }
    const T = this.T, size = r.getDrawingBufferSize(new T.Vector2());
    if (this.colorRT.width !== size.x || this.colorRT.height !== size.y) {
      this.colorRT.setSize(size.x, size.y); this.normalRT.setSize(size.x, size.y);
      this.mat.uniforms.res.value.copy(size);
    }
    this.mat.uniforms.near.value = camera.near; this.mat.uniforms.far.value = camera.far;
    this.mat.uniforms.k.value = this.lineScale * size.y / 320 / Math.max(1, r.getPixelRatio());
    const bg = scene.background, tm = r.toneMapping;
    r.toneMapping = T.NoToneMapping;
    r.setRenderTarget(this.colorRT); r.render(scene, camera);
    scene.background = null; scene.overrideMaterial = this.normalMat;
    r.setRenderTarget(this.normalRT); r.setClearColor(0x8080ff, 1); r.render(scene, camera);
    scene.overrideMaterial = null; scene.background = bg; r.toneMapping = tm;
    r.setRenderTarget(null);
    r.render(this.quadScene, this.quadCam);
  }
}
export function lookFromUrl() { return new URLSearchParams(location.search).get('look') === 'ink'; }
export function setLookInUrl(on) {
  const q = new URLSearchParams(location.search);
  if (on) q.set('look', 'ink'); else q.delete('look');
  const s = q.toString(); history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash);
}
