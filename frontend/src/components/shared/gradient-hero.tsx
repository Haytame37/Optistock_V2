"use client"

import { cn } from "@/lib/utils"

interface GradientHeroProps {
  title: string
  subtitle?: string
  children?: React.ReactNode
  className?: string
}

export function GradientHero({ title, subtitle, children, className }: GradientHeroProps) {
  return (
    <div
      className={cn(
        "rounded-2xl p-6 gradient-hero-light mb-4",
        className
      )}
    >
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      {subtitle && <p className="mt-1 max-w-2xl text-white/80 text-sm">{subtitle}</p>}
      {children}
    </div>
  )
}
