import {Composition} from 'remotion';
import {Promo, promoDefaults, promoMetadata} from './Promo';
import {StyleCinema} from './styles/Cinema';
import {StyleStudio} from './styles/Studio';
import {styleMetadata} from './styles/commun';
import type {StyleProps} from './styles/commun';

// Every composition a job can name. Size and frame rate are fixed per composition;
// the duration may come from props (calculateMetadata).
export const Root = () => (
  <>
    <Composition
      id="Promo"
      component={Promo}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={150}
      defaultProps={promoDefaults}
      calculateMetadata={promoMetadata}
    />
    {/* Style teasers: all their data comes from the job (no defaults to show without one). */}
    <Composition
      id="StyleCinema"
      component={StyleCinema}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={240}
      defaultProps={{} as StyleProps}
      calculateMetadata={styleMetadata}
    />
    <Composition
      id="StyleStudio"
      component={StyleStudio}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={240}
      defaultProps={{} as StyleProps}
      calculateMetadata={styleMetadata}
    />
  </>
);
