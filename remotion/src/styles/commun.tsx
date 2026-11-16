// Shared by the style teasers (Cinema, Studio): props, fonts, logo, music, timing.
// Every word, colour, picture and geometry point comes from the job's props.
import {useEffect, useState} from 'react';
import {AbsoluteFill, Easing, Img, cancelRender, continueRender, delayRender, interpolate, staticFile, useVideoConfig} from 'remotion';
import type {CalculateMetadataFunction, EffectsProp} from 'remotion';
import {Audio} from '@remotion/media';
import {loadFont} from '@remotion/fonts';

export type Point = [number, number]; // percent of the source picture (x, y)
export type Photo = {src: string; taille: [number, number]; foyer: Point; lumiere: Point};
export type Plan = {titre: string[]; or?: string; image: Photo};
export type Cote = {texte: string; de: Point; a: Point; reperes?: [Point, Point]}; // reperes: the product points each end measures
export type Matiere = {nom: string; image: Photo; centre: Point; rayon: number; cible: Point}; // rayon: on-screen radius, px
export type StyleProps = {
  marque: {
    couleurs: {encre: string; creme: string; or: string; gris: string; brun: string};
    logo: string;
    musique: string;
    polices: {titre: string; titreItalique: string; texte: string; texteFort: string};
    garanties: string[];
    adresse: string;
  };
  produit: {
    nom: string;
    type: string;
    plans: Plan[];
    detoure?: Photo & {boite: [number, number, number, number]};
    cotes?: Cote[];
    matieres?: Matiere[];
  };
  // Seconds: when plans 2, 3… start, when the end card starts, when the video ends.
  temps: {coupes: number[]; carte: number; fin: number};
};

export const FPS = 30;
export const W = 1080;
export const H = 1920;
export const f = (s: number) => Math.round(s * FPS);

export const styleMetadata: CalculateMetadataFunction<StyleProps> = ({props}) => ({
  durationInFrames: f(props.temps?.fin ?? 8), // 8 s when listed without a job
});

export const media = (p: string) => (/^https?:\/\//.test(p) ? p : staticFile(p));

// Brand fonts are files staged by the job; the families get neutral names here.
export const FONTES = {titre: 'MarqueTitre', titreItalique: 'MarqueTitreItalique', texte: 'MarqueTexte', texteFort: 'MarqueTexteFort'};
// Holds the render until the fonts are in; true from then on (text can be measured).
export const usePolices = (p: StyleProps['marque']['polices']) => {
  const [attente] = useState(() => delayRender('brand fonts'));
  const [pret, setPret] = useState(false);
  useEffect(() => {
    Promise.all((Object.keys(FONTES) as (keyof typeof FONTES)[]).map((k) => loadFont({family: FONTES[k], url: media(p[k])})))
      .then(() => {
        setPret(true);
        continueRender(attente);
      })
      .catch((e) => cancelRender(e));
  }, [attente, p]);
  return pret;
};

export const clampE = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const ease = {
  sortie: Easing.bezier(0.16, 1, 0.3, 1), // expo.out: arrivals land on a long tail
  entree: Easing.bezier(0.7, 0, 0.84, 0), // expo.in: exits accelerate
  douce: Easing.bezier(0.65, 0, 0.35, 1), // camera moves, both ways
};
// 0 → 1 between two times in seconds.
export const prog = (frame: number, de: number, duree: number, easing = ease.sortie) =>
  interpolate(frame, [f(de), f(de) + Math.max(1, f(duree))], [0, 1], {...clampE, easing});

// Plan shown at a frame, from the cut list.
export const planA = (frame: number, coupes: number[]) => coupes.filter((c) => frame >= f(c)).length;

// The brand logo as a mask, so it takes any colour.
export const Logo: React.FC<{src: string; couleur: string; largeur: number; style?: React.CSSProperties}> = ({src, couleur, largeur, style}) => (
  <div
    style={{
      width: largeur,
      aspectRatio: '2060 / 1436',
      background: couleur,
      WebkitMaskImage: `url(${media(src)})`,
      WebkitMaskSize: 'contain',
      WebkitMaskRepeat: 'no-repeat',
      WebkitMaskPosition: 'center',
      ...style,
    }}
  />
);

// Same music for every style: no fade-in (its attack is at 0 s), fade-out over the last 0.8 s.
export const Musique: React.FC<{src: string}> = ({src}) => {
  const {durationInFrames} = useVideoConfig();
  return <Audio src={media(src)} volume={(fr) => interpolate(fr, [durationInFrames - f(0.8), durationInFrames], [1, 0], clampE)} />;
};

// Where a photo lands in a w × h box when its point (cx, cy in percent) is centred, at scale s (≤ 1):
// top-left corner, drawn size, and the lamp's position on screen. No edge of the photo ever shows.
export const poser = (photo: Photo, w: number, h: number, s: number, cx: number, cy: number) => {
  const [pw, ph] = photo.taille;
  const sc = Math.min(s, 1); // never more than one source pixel per output pixel
  const iw = pw * sc;
  const ih = ph * sc;
  const x = Math.min(0, Math.max(w - iw, w / 2 - (cx / 100) * iw));
  const y = Math.min(0, Math.max(h - ih, h / 2 - (cy / 100) * ih));
  return {x, y, iw, ih, lx: x + (photo.lumiere[0] / 100) * iw, ly: y + (photo.lumiere[1] / 100) * ih};
};

export const Cadre: React.FC<{
  photo: Photo;
  w: number;
  h: number;
  s: number;
  cx: number;
  cy: number;
  effects?: EffectsProp;
  style?: React.CSSProperties;
  children?: React.ReactNode;
}> = ({photo, w, h, s, cx, cy, effects, style, children}) => {
  const {x, y, iw, ih} = poser(photo, w, h, s, cx, cy);
  return (
    <div style={{position: 'absolute', width: w, height: h, overflow: 'hidden', ...style}}>
      {/* Moved and scaled by a transform, not left/top/width: sub-pixel steps, so a slow move never judders. */}
      <Img
        src={media(photo.src)}
        effects={effects}
        style={{position: 'absolute', left: 0, top: 0, width: photo.taille[0], height: photo.taille[1], transformOrigin: '0 0', transform: `translate3d(${x}px, ${y}px, 0) scale(${iw / photo.taille[0]})`}}
      />
      {children}
    </div>
  );
};

// Words of a title line, the accent word(s) in a colour.
export const Mots: React.FC<{ligne: string; or?: string; couleur: string}> = ({ligne, or, couleur}) => {
  const cle = (t: string) => t.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]/g, '');
  const cibles = new Set((or ?? '').split(/\s+/).map(cle).filter(Boolean));
  return (
    <>
      {ligne.split(/(\s+)/).map((m, i) => (
        <span key={i} style={cibles.has(cle(m)) ? {color: couleur} : undefined}>
          {m}
        </span>
      ))}
    </>
  );
};

export const Fond: React.FC<{couleur: string}> = ({couleur}) => <AbsoluteFill style={{background: couleur}} />;
