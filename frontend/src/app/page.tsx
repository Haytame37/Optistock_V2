"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/layout/theme-toggle"
import { motion } from "framer-motion"
import { ArrowRight, BarChart3, Briefcase, MapPin, Package, Search, Shield, ShieldCheck, Sparkles, TrendingUp, Users } from "lucide-react"

const features = [
  {
    icon: Search,
    title: "Recherche intelligente",
    description: "Trouvez l'entrepôt le plus adapté grâce à notre scoring IA, combinant logistique et conformité IoT.",
  },
  {
    icon: Shield,
    title: "Sécurité réglementaire",
    description: "Surveillez les exigences HACCP et chaîne du froid avec des alertes temps réel sur les anomalies.",
  },
  {
    icon: BarChart3,
    title: "Analyse décisionnelle",
    description: "Comparez les sites selon des métriques claires et prenez des décisions basées sur des données concrètes.",
  },
  {
    icon: Package,
    title: "Optimisation de réseau",
    description: "Choisissez l’implantation la plus performante et diminuez les coûts logistiques et environnementaux.",
  },
]

const steps = [
  { title: "Importer vos besoins", description: "Chargez vos points de livraison et vos exigences produit en quelques clics." },
  { title: "Évaluer vos entrepôts", description: "Analysez chaque site selon les performances logistiques et environnementales." },
  { title: "Prendre la meilleure décision", description: "Bénéficiez d’un score unique et d’une recommandation claire pour vos implantations." },
]

const team = [
  { name: "Atmane Salah", role: "Lead Data & Logistique" },
  { name: "Rafiki Najat", role: "Responsable UX/UI & Auth" },
  { name: "ElAtraoui Haytame", role: "Architecte API & Optimisation" },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-sky-50 to-white text-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      <header className="sticky top-0 z-30 border-b border-slate-200/70 bg-white/90 backdrop-blur-xl dark:border-slate-800/60 dark:bg-slate-950/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground font-bold">OS</div>
            <div>
              <p className="font-display text-lg font-semibold">OptiStock</p>
              <p className="text-xs text-muted-foreground">Système d’aide à la décision logistique</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="outline">Connexion</Button>
            </Link>
            <Link href="/signup">
              <Button>Créer un compte</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-16 lg:py-24">
        <section className="relative overflow-hidden rounded-[2rem] border border-slate-200/80 bg-white/90 p-8 shadow-xl shadow-slate-200/40 dark:border-slate-800/70 dark:bg-slate-950/80 dark:shadow-black/10">
          <div className="absolute inset-0 opacity-40 mix-blend-screen">
            <svg viewBox="0 0 1200 600" className="h-full w-full" preserveAspectRatio="none">
              <defs>
                <linearGradient id="landing-gradient" x1="0" x2="1" y1="0" y2="1">
                  <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#38bdf8" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path d="M0 200C200 120 400 320 600 260C800 200 1000 80 1200 140V600H0Z" fill="url(#landing-gradient)" />
              <circle cx="240" cy="140" r="80" fill="#38bdf8" fillOpacity="0.15" />
              <circle cx="980" cy="120" r="100" fill="#0ea5e9" fillOpacity="0.12" />
            </svg>
          </div>

          <div className="relative grid gap-10 lg:grid-cols-[1.2fr_0.8fr] lg:items-center">
            <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6 }}>
              <p className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1 text-sm font-semibold text-primary shadow-sm">
                <Sparkles className="h-4 w-4" /> Nouveau
              </p>
              <h1 className="mt-8 text-5xl font-black tracking-tight text-slate-950 dark:text-white sm:text-6xl">
                OptiStock, l’outil qui transforme vos décisions logistiques en actions précises.
              </h1>
              <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600 dark:text-slate-300">
                Analyse IoT, scoring multi-critères, et recommandations intelligentes pour choisir l'entrepôt le plus fiable, le plus proche et le mieux noté.
              </p>
              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <Link href="/signup">
                  <Button size="lg">Commencer avec OptiStock</Button>
                </Link>
                <Link href="/login">
                  <Button variant="outline" size="lg">Se connecter</Button>
                </Link>
              </div>
            </motion.div>

            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 0.1 }} className="relative overflow-hidden rounded-[1.75rem] border border-slate-200/80 bg-slate-50 p-8 shadow-xl dark:border-slate-800/70 dark:bg-slate-900/80">
              <div className="absolute right-4 top-4 h-28 w-28 rounded-full bg-primary/10 blur-3xl" />
              <div className="absolute left-4 bottom-8 h-24 w-24 rounded-full bg-sky-400/10 blur-3xl" />
              <div className="relative flex h-full flex-col justify-between gap-6">
                <div className="space-y-4">
                  <p className="text-sm uppercase tracking-[0.25em] text-slate-500 dark:text-slate-400">Décoration du tableau de bord</p>
                  <h2 className="text-2xl font-semibold text-slate-950 dark:text-slate-100">Vue claire & metrics instantanées</h2>
                  <p className="text-sm leading-6 text-slate-600 dark:text-slate-300">
                    Visualisez les scores logistiques, les alertes IoT et les performances d’entrepôt sur un tableau de bord moderne et réactif.
                  </p>
                </div>
                <div className="rounded-[1.5rem] border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950">
                  <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                    <span>Score global</span>
                    <span className="font-semibold text-slate-900 dark:text-white">87%</span>
                  </div>
                  <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                    <div className="h-full w-[87%] rounded-full bg-gradient-to-r from-primary to-sky-500" />
                  </div>
                  <div className="mt-5 grid gap-3 text-sm text-slate-600 dark:text-slate-300">
                    <div className="flex items-center justify-between">
                      <span>Analyse IoT</span>
                      <span>92%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Distance logistique</span>
                      <span>81%</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="mt-16 grid gap-10 lg:grid-cols-2">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-3 rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 dark:bg-slate-900 dark:text-slate-300">
              <Sparkles className="h-4 w-4" /> Conçu par l’équipe OptiStock
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-950 dark:text-white">Une plateforme pensée pour les décideurs logistiques.</h2>
            <p className="max-w-xl text-base leading-7 text-slate-600 dark:text-slate-300">
              Chaque module a été conçu pour donner aux chercheurs, propriétaires et responsables logistiques un accès immédiat à des informations fiables et actionnables.
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              {features.map((feature, index) => (
                <div key={index} className="glass-card border-slate-200/80 p-5 dark:border-slate-800/70">
                  <feature.icon className="h-6 w-6 text-primary mb-3" />
                  <h3 className="font-semibold text-lg text-slate-950 dark:text-white">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[2rem] border border-slate-200/75 bg-slate-50 p-8 shadow-xl dark:border-slate-800/70 dark:bg-slate-900/80">
            <h3 className="text-xl font-semibold text-slate-950 dark:text-white">Comment fonctionne OptiStock ?</h3>
            <div className="mt-8 space-y-6">
              {steps.map((step, index) => (
                <div key={index} className="flex gap-4 rounded-3xl border border-slate-200/70 bg-white/80 p-5 shadow-sm dark:border-slate-800/70 dark:bg-slate-950/90">
                  <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-primary/10 text-primary font-semibold">0{index + 1}</div>
                  <div>
                    <h4 className="font-semibold text-slate-950 dark:text-white">{step.title}</h4>
                    <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-16 rounded-[2rem] border border-slate-200/75 bg-white/90 p-8 shadow-xl dark:border-slate-800/70 dark:bg-slate-950/80">
          <div className="mb-8">
            <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Cas d’usage</p>
            <h2 className="mt-3 text-3xl font-bold text-slate-950 dark:text-white">Illustrations concrètes de l’utilisation d’OptiStock</h2>
          </div>
          <div className="grid gap-6 xl:grid-cols-3">
            <div className="glass-card rounded-[1.75rem] border-slate-200/80 p-6 dark:border-slate-800/70">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-3xl bg-sky-100 text-sky-600 dark:bg-sky-400/10 dark:text-sky-300">
                <Search className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-slate-950 dark:text-white">Chercheur d’entrepôt</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Un analyste charge les points de livraison, calcule le centre de gravité et compare plusieurs sites. Il identifie rapidement l’entrepôt optimal selon la distance, le score IoT et la conformité aux normes HACCP.
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm font-medium text-primary">
                <ShieldCheck className="h-4 w-4" />
                Gain de temps et choix fiable
              </div>
            </div>
            <div className="glass-card rounded-[1.75rem] border-slate-200/80 p-6 dark:border-slate-800/70">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-3xl bg-emerald-100 text-emerald-600 dark:bg-emerald-400/10 dark:text-emerald-300">
                <MapPin className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-slate-950 dark:text-white">Propriétaire d’entrepôt</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Un propriétaire consulte les états de température et d’humidité de ses entrepôts. Il reçoit des alertes saisonnières et peut prouver la conformité de ses sites face aux exigences réglementaires.
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm font-medium text-primary">
                <Briefcase className="h-4 w-4" />
                Transparence et réactivité accrues
              </div>
            </div>
            <div className="glass-card rounded-[1.75rem] border-slate-200/80 p-6 dark:border-slate-800/70">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-3xl bg-violet-100 text-violet-600 dark:bg-violet-400/10 dark:text-violet-300">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold text-slate-950 dark:text-white">Responsable logistique</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
                Le manager compare les coûts de transport et la qualité des sites. Il choisit la meilleure combinaison distance/conformité pour optimiser son réseau de stockage.
              </p>
              <div className="mt-4 flex items-center gap-2 text-sm font-medium text-primary">
                <Shield className="h-4 w-4" />
                Décisions stratégiques et économiques
              </div>
            </div>
          </div>
        </section>

        <section className="mt-16 rounded-[2rem] border border-slate-200/75 bg-white/90 p-8 shadow-xl dark:border-slate-800/70 dark:bg-slate-950/80">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-500 dark:text-slate-400">Équipe OptiStock</p>
              <h2 className="mt-3 text-3xl font-bold text-slate-950 dark:text-white">Une équipe dédiée à votre succès logistique</h2>
            </div>
            <Button size="lg" variant="outline" className="max-w-xs">Découvrir notre approche</Button>
          </div>
          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {team.map((member) => (
              <div key={member.name} className="glass-card rounded-[1.75rem] p-6 text-slate-900 dark:text-white">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-3xl bg-primary/10 text-primary text-xl font-semibold">{member.name.split(" ")[0][0]}</div>
                <h3 className="text-lg font-semibold">{member.name}</h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{member.role}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-16 rounded-[2rem] border border-slate-200/75 bg-slate-50 p-8 text-slate-950 shadow-xl dark:border-slate-800/70 dark:bg-slate-900/80 dark:text-white">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="text-3xl font-bold">Prêt à découvrir votre meilleur réseau d'entrepôts ?</h2>
              <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300">
                Rejoignez la plateforme OptiStock pour piloter vos décisions logistiques avec une vision claire et des recommandations calculées.
              </p>
            </div>
            <Link href="/signup" className="inline-flex items-center gap-2">
              <Button size="lg">Créer mon compte</Button>
              <ArrowRight className="h-5 w-5" />
            </Link>
          </div>
        </section>
      </main>
    </div>
  )
}
