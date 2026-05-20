import { cn } from "@/lib/utils"

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function GlassCard({ children, className, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-white/20 dark:border-white/10 bg-white/80 dark:bg-black/30 backdrop-blur-xl shadow-lg",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
