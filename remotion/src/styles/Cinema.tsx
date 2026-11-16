// Style 4, "evening cinema": letterbox, slow dolly moves, warm glow from the lamp, film grain,
// light leaks, subtitle-style text, film-burn / cross-zoom transitions (HTML-in-canvas).
import {AbsoluteFill, Sequence, Solid, interpolate, useCurrentFrame} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import type {TransitionPresentation} from '@remotion/transitions';
import {filmBurn} from '@remotion/transitions/film-burn';
import {crossZoom} from '@remotion/transitions/cross-zoom';
import {fade} from '@remotion/transitions/fade';
import {noise2D} from '@remotion/noise';
import {lightLeak} from '@remotion/effects/light-leak';
import {Cadre, FONTES, Logo, Mots, Musique, W, clampE, ease, f, planA, poser, prog, usePolices} from './commun';
import type {Plan, StyleProps} from './commun';

const BANDE = {y: 400, h: 1120}; // the picture between the bars; the bars open from 470 px at the start
const TRANSITIONS = [18, 16, 18]; // frames of each seam, centred on its cut

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

let tuile: string | null = null;
const grain = () => {
  if (tuile) return tuile;
  const c = document.createElement('canvas');
  c.width = 384;
  c.height = 384;
  const ctx = c.getContext('2d')!;
  const img = ctx.createImageData(384, 384);
  let g = 12345; // seeded: the same grain on every render
  for (let i = 0; i < img.data.length; i += 4) {
    g = (g * 16807) % 2147483647;
    const v = 128 + ((g / 2147483647 - 0.5) * 2) * 90;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = v;
    img.data[i + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  tuile = c.toDataURL('image/png');
  return tuile;
};

// Slow dolly in, constant speed from the first frame to the last: never a stop.
const vueDolly = (plan: Plan, image: number, duree: number) => {
  const [pw, ph] = plan.image.taille;
  const u = image / duree;
  const s = Math.max(W / pw, BANDE.h / ph) + 0.01 + 0.045 * u;
  const [fx, fy] = plan.image.foyer;
  const [lx, ly] = plan.image.lumiere;
  const drift = (seed: string) => noise2D(seed, image / 75, 0) * 0.5; // a hand-held breath, ±0.5 %
  return {s, cx: lerp(fx, lx, 0.35 * u) + drift('x'), cy: lerp(fy, ly, 0.35 * u) + drift('y')};
};

const Lueur: React.FC<{x: number; y: number; force: number}> = ({x, y, force}) => (
  <div
    style={{
      position: 'absolute',
      left: x - 420,
      top: y - 420,
      width: 840,
      height: 840,
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(255,214,150,0.5) 0%, rgba(255,186,110,0.16) 38%, rgba(255,170,90,0) 70%)',
      mixBlendMode: 'screen',
      opacity: force,
    }}
  />
);

const Prise: React.FC<{plan: Plan; duree: number; flare?: boolean}> = ({plan, duree, flare}) => {
  const image = useCurrentFrame();
  const v = vueDolly(plan, image, duree);
  const {lx, ly} = poser(plan.image, W, BANDE.h, v.s, v.cx, v.cy);
  const souffle = 0.85 + 0.15 * noise2D('lueur', image / 40, 1);
  // Anamorphic streak through the lamp on the first music accent.
  const trait = flare ? interpolate(image, [f(0.45), f(0.9), f(1.9)], [0, 1, 0], clampE) : 0;
  return (
    <AbsoluteFill>
      <Cadre photo={plan.image} w={W} h={BANDE.h} s={v.s} cx={v.cx} cy={v.cy} />
      {/* Evening grade: warm the picture, darken its edges. */}
      <AbsoluteFill style={{background: '#ff9a4a', mixBlendMode: 'soft-light', opacity: 0.32}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse 75% 70% at 50% 46%, rgba(0,0,0,0) 55%, rgba(10,5,0,0.55) 100%)'}} />
      <Lueur x={lx} y={ly} force={souffle} />
      {trait > 0 ? (
        <div
          style={{
            position: 'absolute',
            left: lx - 560 * trait,
            top: ly - 3,
            width: 1120 * trait,
            height: 6,
            borderRadius: 3,
            background: 'linear-gradient(90deg, rgba(255,200,140,0), rgba(255,236,205,0.95), rgba(255,200,140,0))',
            boxShadow: '0 0 28px 8px rgba(255,190,120,0.45)',
            mixBlendMode: 'screen',
            opacity: trait,
          }}
        />
      ) : null}
    </AbsoluteFill>
  );
};

const Carte: React.FC<{p: StyleProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {couleurs: c} = p.marque;
  const monte = (k: number, opacite = 1) => {
    const t = prog(frame, 0.25 + k * 0.14, 0.9);
    return {opacity: t * opacite, transform: `translateY(${(1 - t) * 24}px)`};
  };
  const filet = prog(frame, 0.7, 0.8, ease.douce);
  const texte = {fontFamily: FONTES.texte, color: c.creme, textAlign: 'center' as const};
  return (
    <AbsoluteFill style={{background: '#000', alignItems: 'center'}}>
      <Lueur x={W / 2} y={260} force={0.55} />
      <div style={{position: 'absolute', top: 70, ...monte(0)}}>
        <Logo src={p.marque.logo} couleur={c.creme} largeur={230} />
      </div>
      <div style={{position: 'absolute', top: 270, fontFamily: FONTES.titre, fontSize: 150, letterSpacing: '0.04em', color: c.creme, ...monte(1)}}>
        {p.produit.nom}
      </div>
      <div style={{position: 'absolute', top: 470, fontSize: 40, ...texte, ...monte(2, 0.85)}}>{p.produit.type}</div>
      <div style={{position: 'absolute', top: 552, width: 140 * filet, height: 2, background: c.or}} />
      <div style={{position: 'absolute', top: 594, fontSize: 36, lineHeight: 1.55, ...texte, ...monte(3, 0.9)}}>
        {p.marque.garanties.map((g) => (
          <div key={g}>{g}</div>
        ))}
      </div>
      <div style={{position: 'absolute', top: 830, fontSize: 38, letterSpacing: '0.04em', ...texte, color: c.or, ...monte(4)}}>
        {p.marque.adresse}
      </div>
    </AbsoluteFill>
  );
};

// Subtitles: cut with the shots (6-frame fades), the first one on screen at frame 0.
const SousTitres: React.FC<{p: StyleProps}> = ({p}) => {
  const frame = useCurrentFrame();
  const {coupes, carte} = p.temps;
  const k = planA(frame, coupes);
  const plan = p.produit.plans[k];
  const debut = k === 0 ? -1 : f(coupes[k - 1]);
  const fin = k < coupes.length ? f(coupes[k]) : f(carte);
  const o = interpolate(frame, [debut, debut + 6, fin - 7, fin - 1], [k === 0 ? 1 : 0, 1, 1, 0], clampE);
  if (!plan || frame >= f(carte)) return null;
  return (
    <div
      style={{
        position: 'absolute',
        top: 196,
        width: W,
        textAlign: 'center',
        fontFamily: FONTES.texte,
        fontSize: 54,
        lineHeight: 1.3,
        color: p.marque.couleurs.creme,
        textShadow: '0 2px 14px rgba(0,0,0,0.85), 0 0 3px rgba(0,0,0,0.6)',
        opacity: o,
      }}
    >
      {plan.titre.map((l) => (
        <div key={l}>
          <Mots ligne={l} or={plan.or} couleur={p.marque.couleurs.or} />
        </div>
      ))}
    </div>
  );
};

export const StyleCinema: React.FC<StyleProps> = (p) => {
  usePolices(p.marque.polices);
  const frame = useCurrentFrame();
  const {coupes, carte, fin} = p.temps;
  const bords = [0, ...coupes, carte].map(f);
  const presentations: TransitionPresentation<Record<string, unknown>>[] = [
    filmBurn({seed: 7}) as TransitionPresentation<Record<string, unknown>>,
    crossZoom({strength: 0.4}) as TransitionPresentation<Record<string, unknown>>, // dreamyZoom dips to white: not for an evening
    fade() as TransitionPresentation<Record<string, unknown>>,
  ];
  // Each piece lasts from its start to its cut, plus half of each seam it shares.
  const demi = (i: number) => Math.round(TRANSITIONS[i % TRANSITIONS.length] / 2);
  const morceaux = p.produit.plans.map((plan, i) => ({plan, duree: bords[i + 1] - bords[i] + (i ? demi(i - 1) : 0) + demi(i)}));
  const dureeCarte = f(fin) - f(carte) + demi(p.produit.plans.length - 1);
  const ouverture = prog(frame, 0, 1.2, ease.douce);
  const barre = lerp(BANDE.y + 70, BANDE.y, ouverture);
  const credit = prog(frame, 0.5, 0.9);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <div style={{position: 'absolute', top: BANDE.y, width: W, height: BANDE.h, overflow: 'hidden'}}>
        <TransitionSeries>
          {morceaux.map((m, i) => [
            <TransitionSeries.Sequence key={`p${i}`} durationInFrames={m.duree}>
              <Prise plan={m.plan} duree={m.duree} flare={i === 0} />
            </TransitionSeries.Sequence>,
            <TransitionSeries.Transition
              key={`t${i}`}
              presentation={presentations[i % presentations.length]}
              timing={linearTiming({durationInFrames: 2 * demi(i)})}
            />,
          ])}
          <TransitionSeries.Sequence durationInFrames={dureeCarte}>
            <Carte p={p} />
          </TransitionSeries.Sequence>
        </TransitionSeries>
        {/* Light leaks breathe over each seam; grain over the whole picture. */}
        {bords.slice(1).map((b, i) => (
          <Sequence key={b} from={b - 12} durationInFrames={30} layout="none">
            <Fuite seed={i + 2} />
          </Sequence>
        ))}
        {/* Film grain: one seeded noise tile, made once per browser tab, shifted to a new place every frame.
            (A noise drawn anew each frame, effect or SVG, cost 2 to 4 s per frame on the runner.) */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `url(${grain()})`,
            backgroundSize: '768px 768px',
            backgroundPosition: `${(frame * 7919) % 768}px ${(frame * 104729) % 768}px`,
            mixBlendMode: 'overlay',
            opacity: 0.3,
          }}
        />
      </div>
      <div style={{position: 'absolute', top: 0, width: W, height: barre, background: '#000'}} />
      <div style={{position: 'absolute', top: BANDE.y + BANDE.h + (BANDE.y - barre), width: W, bottom: 0, background: '#000'}} />
      <SousTitres p={p} />
      <div
        style={{
          position: 'absolute',
          top: BANDE.y + BANDE.h + 40,
          width: W,
          textAlign: 'center',
          fontFamily: FONTES.texte,
          fontSize: 28,
          letterSpacing: '0.6em',
          textTransform: 'uppercase',
          color: p.marque.couleurs.or,
          opacity: credit * (frame < f(carte) ? 1 : 1 - prog(frame, carte, 0.4)),
        }}
      >
        {p.produit.nom}
      </div>
      <Musique src={p.marque.musique} />
    </AbsoluteFill>
  );
};

const Fuite: React.FC<{seed: number}> = ({seed}) => {
  const image = useCurrentFrame();
  const t = image / 30;
  const montee = Math.sin(Math.PI * t);
  // Only the first third of the leak's evolution: a glow from the edge, never a frame washed white.
  return (
    <Solid
      width={W / 2}
      height={BANDE.h / 2}
      color="transparent"
      effects={[lightLeak({seed, hueShift: 20, progress: 0.32 * montee})]}
      style={{position: 'absolute', left: 0, top: 0, width: W, height: BANDE.h, mixBlendMode: 'screen', opacity: 0.55 * montee}}
    />
  );
};
