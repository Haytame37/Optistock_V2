import { cn } from "@/lib/utils"

interface KpiCardProps {
  label: string
  value: string | number
  icon?: string
  subtitle?: string
  className?: string
  color?: string
}

export function KpiCard({ label, value, icon, subtitle, className, color }: KpiCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border bg-card p-4 shadow-sm transition-all hover:shadow-md",
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-bold" style={color ? { color } : undefined}>
            {value}
          </p>
          {subtitle && <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
    </div>
  )
}
