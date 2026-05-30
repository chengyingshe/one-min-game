import { LOCATION_META } from "@/lib/constants";
import SvgScene from "./SvgScene";

type Props = {
  locationKey: string;
  children?: React.ReactNode;
};

const SCENE_GRADIENTS: Record<string, string> = {
  teahouse: "from-amber-100 via-orange-50 to-yellow-50",
  market: "from-red-50 via-amber-50 to-orange-50",
  academy: "from-stone-100 via-emerald-50 to-teal-50",
  riverside: "from-sky-50 via-blue-50 to-indigo-50",
};

export default function SceneBackground({ locationKey, children }: Props) {
  const meta = LOCATION_META[locationKey] || {
    emoji: "🏠",
    display: locationKey,
  };
  const gradient = SCENE_GRADIENTS[locationKey] || SCENE_GRADIENTS.teahouse;

  return (
    <SvgScene
      sceneName={locationKey}
      fallbackGradient={gradient}
      fallbackEmoji={meta.emoji}
    >
      {/* Location label */}
      <div className="absolute top-3 left-3 rounded-full bg-black/40 px-3 py-1 text-sm text-white backdrop-blur-sm">
        {meta.emoji} {meta.display}
      </div>

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </SvgScene>
  );
}
