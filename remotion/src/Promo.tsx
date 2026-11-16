import {AbsoluteFill, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {CalculateMetadataFunction} from 'remotion';
import {Audio} from '@remotion/media';
import {loadFont as loadPlayfair} from '@remotion/google-fonts/PlayfairDisplay';
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';

// Vertical product promo. Every word, colour and media file comes from the job's props:
// nothing here belongs to a shop. Same prop names as hyperframes/promo/index.html.
const {fontFamily: serif} = loadPlayfair('normal', {weights: ['400'], subsets: ['latin']});
const {fontFamily: sans} = loadInter('normal', {weights: ['400', '500'], subsets: ['latin']});

export type PromoProps = {
  eyebrow: string;
  title: string;
  subtitle: string;
  image: string; // staged file (assets/job/…) or https URL
  music: string; // staged file (assets/job/…) or https URL; '' = silent
  background: string;
  ink: string;
  accent: string;
  seconds?: number;
};

export const promoDefaults: PromoProps = {
  eyebrow: 'Eyebrow',
  title: 'Title',
  subtitle: 'Subtitle',
  image: 'assets/job/photo.jpg',
  music: 'assets/job/music.m4a',
  background: '#111111',
  ink: '#ffffff',
  accent: '#d4d4d4',
  seconds: 5,
};

export const promoMetadata: CalculateMetadataFunction<PromoProps> = ({props}) => ({
  durationInFrames: Math.round((props.seconds ?? 5) * 30),
});

const media = (p: string) => (/^https?:\/\//.test(p) ? p : staticFile(p));
const expoOut = Easing.bezier(0.16, 1, 0.3, 1); // GSAP expo.out
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// 0 → 1 between two frames, eased.
const useProgress = (from: number, length: number, easing = expoOut) =>
  interpolate(useCurrentFrame(), [from, from + length], [0, 1], {...clamp, easing});

// A line that rises from behind a mask.
const Rise: React.FC<{start: number; children: React.ReactNode; style: React.CSSProperties}> = ({
  start,
  children,
  style,
}) => {
  const t = useProgress(start, 27);
  return (
    <div style={{overflow: 'hidden', paddingBottom: '0.12em'}}>
      <div style={{...style, transform: `translate3d(0, ${(1 - t) * 110}%, 0)`}}>{children}</div>
    </div>
  );
};

export const Promo: React.FC<PromoProps> = (p) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();

  const reveal = useProgress(0, 24); // photo opens from an 8 % inset: never a black first frame
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.08]); // constant speed, no stop-start
  const eyebrow = useProgress(4, 18, Easing.out(Easing.cubic));
  const rule = useProgress(18, 24);

  return (
    <AbsoluteFill style={{background: p.background}}>
      <div style={{position: 'absolute', left: 0, top: 600, width: 1080, height: 1080, overflow: 'hidden'}}>
        <div style={{position: 'absolute', inset: 0, clipPath: `inset(${(1 - reveal) * 8}% 0%)`}}>
          <Img
            src={media(p.image)}
            style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`}}
          />
        </div>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(to bottom, ${p.background} 0%, transparent 16%, transparent 78%, ${p.background} 100%)`,
          }}
        />
      </div>

      <div style={{position: 'absolute', left: 84, right: 84, top: 236}}>
        <div
          style={{
            fontFamily: sans,
            fontWeight: 500,
            fontSize: 30,
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            color: p.accent,
            opacity: eyebrow,
            transform: `translate3d(0, ${(1 - eyebrow) * 30}px, 0)`,
          }}
        >
          {p.eyebrow}
        </div>
        <div style={{height: 18}} />
        <Rise start={8} style={{fontFamily: serif, fontSize: 128, lineHeight: 1.05, color: p.ink}}>
          {p.title}
        </Rise>
        <div style={{height: 22}} />
        <div style={{height: 3, width: 160, background: p.accent, transformOrigin: 'left', transform: `scaleX(${rule})`}} />
        <div style={{height: 24}} />
        <Rise start={22} style={{fontFamily: sans, fontSize: 40, lineHeight: 1.2, color: p.ink, opacity: 0.85}}>
          {p.subtitle}
        </Rise>
      </div>

      {p.music ? (
        <Audio
          src={media(p.music)}
          volume={(f) =>
            interpolate(f, [0, 12, durationInFrames - 36, durationInFrames], [0, 0.9, 0.9, 0], clamp)
          }
        />
      ) : null}
    </AbsoluteFill>
  );
};
