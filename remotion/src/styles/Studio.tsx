// Style 5, "product studio": the product cut out on a clean studio wall, parallax depth,
// dimension lines that draw themselves, a context inset, material swatches seen at 1:1 (macro).
import {AbsoluteFill, Img, interpolate, useCurrentFrame} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {clockWipe} from '@remotion/transitions/clock-wipe';
import {evolvePath} from '@remotion/paths';
import {CameraMotionBlur} from '@remotion/motion-blur';
import {noise2D} from '@remotion/noise';
import {fitText} from '@remotion/layout-utils';
import {Cadre, FONTES, Logo, Mots, Musique, H, W, clampE, ease, f, media, planA, prog, usePolices} from './commun';
import type {Point, StyleProps} from './commun';

type Pose = {s: number; x: number; y: number}; // product scale and screen centre of its box
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const POSES: {t: number; pose: Pose}[] = [
  {t: 0, pose: {s: 0.65, x: 500, y: 1000}},
  {t: 2.2, pose: {s: 0.69, x: 505, y: 990}},
  {t: 3.0, pose: {s: 0.48, x: 290, y: 980}},
  {t: 4.3, pose: {s: 0.5, x: 296, y: 972}},
  {t: 5.0, pose: {s: 0.52, x: 360, y: 960}},
];
const poseA = (sec: number): Pose => {
  const i = Math.max(0, POSES.findIndex((p, k) => k === POSES.length - 1 || POSES[k + 1].t > sec));
  const a = POSES[i];
  const b = POSES[Math.min(i + 1, POSES.length - 1)];
  const u = b.t > a.t ? ease.douce(Math.min(1, Math.max(0, (sec - a.t) / (b.t - a.t)))) : 0;
  return {s: lerp(a.pose.s, b.pose.s, u), x: lerp(a.pose.x, b.pose.x, u), y: lerp(a.pose.y, b.pose.y, u)};
};

const Grille: React.FC<{dx: number; dy: number; couleur: string}> = ({dx, dy, couleur}) => (
  <AbsoluteFill
    style={{
      backgroundImage: `linear-gradient(${couleur} 1px, transparent 1px), linear-gradient(90deg, ${couleur} 1px, transparent 1px)`,
      backgroundSize: '72px 72px',
      backgroundPosition: `${dx}px ${dy}px`,
      opacity: 0.07,
      maskImage: 'radial-gradient(ellipse 70% 55% at 50% 48%, #000 30%, transparent 85%)',
    }}
  />
);

// A path that draws itself (evolvePath) between two times.
const Trace: React.FC<{d: string; t: number; style: React.SVGProps<SVGPathElement>}> = ({d, t, style}) => {
  const {strokeDasharray, strokeDashoffset} = evolvePath(t, d);
  return t > 0 ? <path d={d} fill="none" strokeDasharray={strokeDasharray} strokeDashoffset={strokeDashoffset} {...style} /> : null;
};

const Section: React.FC<{p: StyleProps; pret: boolean}> = ({p, pret}) => {
  const frame = useCurrentFrame();
  const sec = frame / 30;
  const {couleurs: c} = p.marque;
  const d = p.produit.detoure!;
  const [pw, ph] = d.taille;
  const pose = poseA(sec);
  const flotte = noise2D('flotte', sec / 3, 0) * 8;
  const s = pose.s;
  const [bx0, by0, bx1, by1] = d.boite;
  const gauche = pose.x - (((bx0 + bx1) / 2) * pw * s) / 100;
  const haut = pose.y - (((by0 + by1) / 2) * ph * s) / 100 + flotte;
  const ecran = (pt: Point): Point => [gauche + (pt[0] / 100) * pw * s, haut + (pt[1] / 100) * ph * s];
  const tourne = interpolate(sec, [0, 6], [-3, 3]);

  // Dimension lines, plan 1.
  const cotes = (p.produit.cotes ?? []).map((cote, i) => {
    const t = prog(frame, 0.5 + i * 0.35, 0.8, ease.douce) * (1 - prog(frame, 2.05, 0.3, ease.entree));
    const [ax, ay] = ecran(cote.de);
    const [bx, by] = ecran(cote.a);
    const len = Math.hypot(bx - ax, by - ay);
    const [ux, uy] = [(bx - ax) / len, (by - ay) / len];
    const [nx, ny] = [-uy * 14, ux * 14];
    const ligne = `M ${ax} ${ay} L ${bx} ${by}`;
    const bouts = `M ${ax + nx} ${ay + ny} L ${ax - nx} ${ay - ny} M ${bx + nx} ${by + ny} L ${bx - nx} ${by - ny}`;
    const reperes = (cote.reperes ?? []).map((r, k) => {
      const [rx, ry] = ecran(r);
      const [ex, ey] = k ? [bx, by] : [ax, ay];
      return `M ${rx} ${ry} L ${ex} ${ey}`;
    });
    const vertical = Math.abs(uy) > Math.abs(ux);
    return {t, ligne, bouts, reperes, mx: (ax + bx) / 2, my: (ay + by) / 2, vertical, texte: cote.texte};
  });

  // Context inset, plan 2.
  const plan2 = p.produit.plans[1];
  const encart = prog(frame, 2.55, 0.6, ease.douce);
  const sortieEncart = prog(frame, 4.2, 0.35, ease.entree);
  const [ex0, ey0] = ecran(d.lumiere);

  // Swatches, plan 3.
  const matieres = p.produit.matieres ?? [];
  // A column on the right; each swatch's displayed radius comes from the job.
  const hauts = matieres.reduce<number[]>((acc, m, i) => [...acc, i ? acc[i - 1] + 2 * matieres[i - 1].rayon + 92 : 540], []);
  const pastilles = matieres.map((m, i) => {
    const arrivee = prog(frame, 4.55 + i * 0.12, 0.55);
    const r = m.rayon;
    const y = hauts[i] + r;
    const x = 822 + (1 - arrivee) * 520;
    const [cx, cy] = ecran(m.cible);
    const fil = prog(frame, 4.95 + i * 0.1, 0.45, ease.douce);
    // Macro: the swatch shows the photo at up to one source pixel per screen pixel, zooming in slowly.
    const zoom = interpolate(sec, [4.5, 6.2], [0.78, 1], clampE);
    return {m, r, x, y, cx, cy, fil, zoom, o: arrivee};
  });

  const titreTaille = (ligne: string) =>
    pret ? Math.min(92, fitText({text: ligne, withinWidth: 900, fontFamily: FONTES.texteFort}).fontSize) : 92;
  const k = planA(frame, p.temps.coupes);
  const plan = p.produit.plans[Math.min(k, p.produit.plans.length - 1)];
  const debutPlan = k ? p.temps.coupes[k - 1] : -1;
  const entre = k ? prog(frame, debutPlan, 0.55) : 1;
  const finPlan = k < p.temps.coupes.length ? p.temps.coupes[k] : p.temps.carte + 1;
  const part = prog(frame, finPlan - 0.28, 0.28, ease.entree); // the title leaves upwards just before its cut

  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse 90% 70% at 50% 42%, ${c.creme} 0%, #e9e3d9 70%, #ddd5c8 100%)`}}>
      <Grille dx={-(pose.x - 540) * 0.3} dy={-flotte * 0.3} couleur={c.encre} />
      {/* The product: soft wall shadow, a slight turn for depth. */}
      <div
        style={{position: 'absolute', left: 0, top: 0, width: pw, height: ph, transformOrigin: '0 0', transform: `translate3d(${gauche}px, ${haut}px, 0) scale(${s})`}}
      >
        <Img
          src={media(d.src)}
          style={{
            width: pw,
            height: ph,
            transform: `perspective(${1800 / s}px) rotateY(${tourne}deg)`,
            filter: `drop-shadow(${26 / s}px ${34 / s}px ${26 / s}px rgba(40,30,20,0.28))`,
          }}
        />
      </div>
      <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
        {cotes.map((q) => (
          <g key={q.texte} opacity={Math.min(1, q.t * 3)}>
            {q.reperes.map((r) => (
              <Trace key={r} d={r} t={q.t} style={{stroke: c.encre, strokeOpacity: 0.45, strokeWidth: 1.5, strokeDasharray: '6 6'}} />
            ))}
            <Trace d={q.ligne} t={q.t} style={{stroke: c.encre, strokeWidth: 2.5}} />
            <Trace d={q.bouts} t={q.t} style={{stroke: c.encre, strokeWidth: 2.5}} />
          </g>
        ))}
        {pastilles.map((q) => (
          <Trace key={q.m.nom} d={`M ${q.x - q.r} ${q.y} L ${q.cx} ${q.cy}`} t={q.fil} style={{stroke: c.brun, strokeWidth: 2}} />
        ))}
        {pastilles.map((q) => (q.fil > 0.98 ? <circle key={q.m.nom} cx={q.cx} cy={q.cy} r={7} fill={c.or} stroke={c.creme} strokeWidth={3} /> : null))}
        {encart > 0 && sortieEncart < 1 ? (
          <Trace d={`M ${ex0} ${ey0} L 560 ${700 + 360}`} t={prog(frame, 3.0, 0.5, ease.douce) * (1 - sortieEncart)} style={{stroke: c.brun, strokeWidth: 2}} />
        ) : null}
      </svg>
      {cotes.map((q) => (
        <div
          key={q.texte}
          style={{
            position: 'absolute',
            left: q.mx + (q.vertical ? 46 : 0),
            top: q.my + (q.vertical ? 0 : -24),
            // A vertical measure reads along its line, as on a technical drawing.
            transform: q.vertical ? 'translate(-50%, -50%) rotate(-90deg)' : 'translate(-50%, -100%)',
            fontFamily: FONTES.texteFort,
            fontSize: 34,
            color: c.encre,
            background: c.creme,
            padding: '6px 14px',
            borderRadius: 8,
            whiteSpace: 'nowrap',
            opacity: interpolate(q.t, [0.55, 0.85], [0, 1], clampE),
          }}
        >
          {q.texte}
        </div>
      ))}
      {plan2 && encart > 0 && sortieEncart < 1 ? (
        <div
          style={{
            position: 'absolute',
            left: 560 + sortieEncart * 600,
            top: 700,
            width: 440,
            height: 720,
            clipPath: `inset(0 ${(1 - encart) * 100}% 0 0)`,
            boxShadow: '0 24px 50px rgba(40,30,20,0.22)',
            outline: `1.5px solid ${c.encre}`,
            outlineOffset: 10,
          }}
        >
          <Cadre photo={plan2.image} w={440} h={720} s={0.62 + 0.04 * prog(frame, 2.5, 2, ease.douce)} cx={plan2.image.lumiere[0]} cy={plan2.image.foyer[1]} />
        </div>
      ) : null}
      <CameraMotionBlur shutterAngle={200} samples={6}>
        <AbsoluteFill>
          {pastilles.map((q) => (
            <div key={q.m.nom} style={{position: 'absolute', left: q.x - q.r, top: q.y - q.r, opacity: Math.min(1, q.o * 2)}}>
              <div
                style={{
                  width: 2 * q.r,
                  height: 2 * q.r,
                  borderRadius: '50%',
                  overflow: 'hidden',
                  position: 'relative',
                  boxShadow: `0 0 0 4px ${c.creme}, 0 0 0 5.5px ${c.or}, 0 18px 36px rgba(40,30,20,0.25)`,
                }}
              >
                <Img
                  src={media(q.m.image.src)}
                  style={{
                    position: 'absolute',
                    width: q.m.image.taille[0] * q.zoom,
                    height: q.m.image.taille[1] * q.zoom,
                    left: q.r - (q.m.centre[0] / 100) * q.m.image.taille[0] * q.zoom,
                    top: q.r - (q.m.centre[1] / 100) * q.m.image.taille[1] * q.zoom,
                  }}
                />
              </div>
              <div
                style={{
                  marginTop: 18,
                  width: 2 * q.r,
                  textAlign: 'center',
                  fontFamily: FONTES.texteFort,
                  fontSize: 32,
                  color: c.encre,
                  opacity: interpolate(q.fil, [0.4, 1], [0, 1], clampE),
                  whiteSpace: 'nowrap',
                }}
              >
                {q.m.nom}
              </div>
            </div>
          ))}
        </AbsoluteFill>
      </CameraMotionBlur>
      {/* Title: the product name as a small kicker, the plan's text below. */}
      <div style={{position: 'absolute', left: 80, top: 214, fontFamily: FONTES.texte, fontSize: 28, letterSpacing: '0.42em', color: c.brun, textTransform: 'uppercase'}}>
        {p.produit.nom}
      </div>
      <div style={{position: 'absolute', left: 80, top: 262, width: 920}}>
        {plan.titre.map((l, i) => {
          const t = (k ? prog(frame, debutPlan + i * 0.08, 0.55) : 1) - part;
          return (
            <div key={`${k}-${i}`} style={{overflow: 'hidden', paddingBottom: 6}}>
              <div
                style={{
                  fontFamily: FONTES.texteFort,
                  fontSize: titreTaille(l),
                  lineHeight: 1.08,
                  color: c.encre,
                  transform: `translateY(${(1 - t) * 105}%)`,
                }}
              >
                <Mots ligne={l} or={plan.or} couleur={c.brun} />
              </div>
            </div>
          );
        })}
      </div>
      <div style={{position: 'absolute', left: 80, top: 252, width: 64 * entre * (1 - part), height: 4, background: c.or}} />
    </AbsoluteFill>
  );
};

const Carte: React.FC<{p: StyleProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {couleurs: c} = p.marque;
  const monte = (k: number) => {
    const t = prog(frame, 0.2 + k * 0.1, 0.6);
    return {opacity: t, transform: `translateY(${(1 - t) * 30}px)`};
  };
  const coche = (i: number) => prog(frame, 0.7 + i * 0.12, 0.35, ease.douce);
  return (
    <AbsoluteFill style={{background: c.creme, alignItems: 'center'}}>
      <div style={{position: 'absolute', top: 330, ...monte(0)}}>
        <Logo src={p.marque.logo} couleur={c.encre} largeur={210} />
      </div>
      <div style={{position: 'absolute', top: 540, fontFamily: FONTES.titre, fontSize: 140, color: c.encre, ...monte(1)}}>{p.produit.nom}</div>
      <div style={{position: 'absolute', top: 730, fontFamily: FONTES.texte, fontSize: 38, color: c.gris, ...monte(2)}}>{p.produit.type}</div>
      <div style={{position: 'absolute', top: 820, width: 120 * prog(frame, 0.5, 0.5), height: 3, background: c.or}} />
      <div style={{position: 'absolute', top: 880, ...monte(3)}}>
        {p.marque.garanties.map((g, i) => (
          <div key={g} style={{display: 'flex', alignItems: 'center', gap: 18, height: 64, fontFamily: FONTES.texte, fontSize: 34, color: c.encre}}>
            <svg width={34} height={34}>
              <circle cx={17} cy={17} r={15} fill="none" stroke={c.or} strokeWidth={2} />
              <Trace d="M 9 17.5 L 15 23 L 25 11" t={coche(i)} style={{stroke: c.brun, strokeWidth: 3, strokeLinecap: 'round', strokeLinejoin: 'round'}} />
            </svg>
            {g}
          </div>
        ))}
      </div>
      <div style={{position: 'absolute', top: 1140, fontFamily: FONTES.texteFort, fontSize: 36, letterSpacing: '0.03em', color: c.brun, ...monte(4)}}>
        {p.marque.adresse}
      </div>
    </AbsoluteFill>
  );
};

export const StyleStudio: React.FC<StyleProps> = (p) => {
  const pret = usePolices(p.marque.polices);
  const {carte, fin} = p.temps;
  const T = 16;
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={f(carte) + T / 2}>
          <Section p={p} pret={pret} />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={clockWipe({width: W, height: H})} timing={linearTiming({durationInFrames: T})} />
        <TransitionSeries.Sequence durationInFrames={f(fin) - f(carte) + T / 2}>
          <Carte p={p} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Musique src={p.marque.musique} />
    </AbsoluteFill>
  );
};
