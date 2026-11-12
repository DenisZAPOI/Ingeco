import type { HelpCategory } from '../../api/helpServices';
import { BasketIcon, FormIcon, HealthIcon, HouseIcon, LaptopIcon, PramIcon, ScalesIcon, ShirtIcon } from '../ui/icons';

const ICONS = {
  childcare: PramIcon,
  housing: HouseIcon,
  rights: ScalesIcon,
  health: HealthIcon,
  food: BasketIcon,
  digital: LaptopIcon,
  paperwork: FormIcon,
  equipment: ShirtIcon,
} as const;

/** The icon of a need of the directory, always next to its name. */
export function CategoryIcon({ category, className }: { category: HelpCategory; className?: string }) {
  const Icon = ICONS[category];
  return <Icon className={className} />;
}
