"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/layout/theme-toggle"
import { motion, AnimatePresence, useReducedMotion } from "framer-motion"
import {
  ArrowRight,
  MapPin,
  Package,
  Search,
  ShieldCheck,
  TrendingUp,
  Database,
  Thermometer,
  Sparkles,
  X
} from "lucide-react"

const dynamicWords = [
  "Réseau de Stockage",
  "Chaîne Logistique",
  "Implantation Industrielle",
  "Monitoring IoT"
]

const CSS_ANIM = `
@keyframes blobDrift{0%,100%{transform:translate(0,0) scale(1)}33%{transform:translate(30px,-30px) scale(1.05)}66%{transform:translate(-20px,20px) scale(0.97)}}
@keyframes particleRise{0%{transform:translateY(0);opacity:.6}100%{transform:translateY(-120vh);opacity:0}}
@keyframes ambientSpin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important}}
`

const PARTICLES = Array.from({ length: 25 }, (_, i) => ({
  id: i, left: `${(i * 37 + 11) % 100}%`, top: `${(i * 53 + 17) % 80 + 10}%`,
  size: (i % 3) + 2, dur: 8 + (i % 8), delay: -(i * .6),
}))

const TEAM_GH = [
  { name: "Atmane Salah", role: "Lead Data & Logistique", gh: "atmansalah019-debug" },
  { name: "Rafiki Najat", role: "Responsable UX/UI & Auth", gh: "rafikinajat1" },
  { name: "ElAtraoui Haytame", role: "Architecte API & Optimisation", gh: "Haytame37" },
]

function GHIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-4 w-4" aria-hidden>
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.438 9.8 8.205 11.387.6.113.82-.258.82-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.09-.744.083-.729.083-.729 1.205.085 1.84 1.237 1.84 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.93 0-1.31.468-2.38 1.235-3.22-.123-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.3 1.23A11.52 11.52 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.29-1.552 3.297-1.23 3.297-1.23.653 1.652.242 2.873.12 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .322.218.694.825.576C20.565 21.796 24 17.298 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
  )
}

function WaveSep({ dark = true, flipY = false }: { dark?: boolean, flipY?: boolean }) {
  return (
    <div className="pointer-events-none w-full overflow-hidden" style={{ height: 48, marginTop: -1 }}>
      <svg viewBox="0 0 1440 48" preserveAspectRatio="none" className="w-full h-full block" style={{ transform: flipY ? "scaleY(-1)" : undefined }}>
        <path d="M0,24 C360,48 1080,0 1440,24 L1440,48 L0,48 Z" fill={dark ? "#0f172a" : "#f8fafc"} opacity=".5" />
        <path d="M0,32 C480,8 960,44 1440,16 L1440,48 L0,48 Z" fill={dark ? "#0f172a" : "#f8fafc"} opacity=".85" />
      </svg>
    </div>
  )
}

function RevealDiv({ children, className = "" }: { children: React.ReactNode, className?: string }) {
  const rm = useReducedMotion()
  return (
    <motion.div className={className}
      initial={rm ? {} : { opacity: 0, y: 30 }}
      whileInView={rm ? {} : { opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: .5 }}
    >{children}</motion.div>
  )
}

export default function LandingPage() {
  const [index, setIndex] = useState(0)
  const [showSimulationVideo, setShowSimulationVideo] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % dynamicWords.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const rm = useReducedMotion()

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
      <style>{CSS_ANIM}</style>
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-white font-bold text-xl shadow-md">OS</div>
            <div>
              <p className="font-bold text-lg leading-tight uppercase tracking-tighter">OptiStock</p>
              <p className="text-[10px] uppercase tracking-widest text-primary font-bold">Solutions Logistiques</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <nav className="hidden md:flex items-center gap-6 text-sm font-bold uppercase tracking-wide">
              {[{ l: "Nos Services", id: "services" }, { l: "La Technologie au Service de Votre Rentabilité", id: "tech" }, { l: "L'Équipe", id: "team" }].map(({ l, id }) => (
                <button key={id} onClick={() => scrollToSection(id)} className="relative group hover:text-primary transition-colors">
                  {l}
                  <span className="absolute -bottom-0.5 left-0 h-0.5 w-full bg-blue-400 scale-x-0 group-hover:scale-x-100 origin-left transition-transform duration-200" />
                </button>
              ))}
            </nav>
            <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden md:block" />
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost" className="font-bold">Se connecter</Button>
            </Link>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link href="/signup">
                <Button className="font-bold px-6">S'inscrire</Button>
              </Link>
            </motion.div>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative h-[85vh] flex items-center overflow-hidden bg-slate-950">
          {/* #9 Ambient rotating ellipse */}
          <div className="absolute inset-0 z-0 pointer-events-none flex items-center justify-center" aria-hidden>
            <div style={{ width: 600, height: 400, opacity: .12, borderRadius: "50%", background: "radial-gradient(ellipse,#3b82f6 0%,transparent 70%)", animation: "ambientSpin 20s linear infinite" }} />
          </div>
          {/* #1 Dot-grid overlay */}
          <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden style={{ opacity: .04, backgroundImage: "radial-gradient(circle,#94a3b8 1px,transparent 1px)", backgroundSize: "24px 24px" }} />
          {/* #1 Color blobs */}
          <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden>
            {[
              { c: "#3b82f6", t: "10%", l: "60%", w: 400, h: 350, dur: "14s", del: "0s" },
              { c: "#6366f1", t: "50%", l: "75%", w: 300, h: 280, dur: "18s", del: "-4s" },
              { c: "#22d3ee", t: "25%", l: "80%", w: 250, h: 220, dur: "22s", del: "-8s" },
            ].map((b, i) => (
              <div key={i} style={{ position: "absolute", top: b.t, left: b.l, width: b.w, height: b.h, borderRadius: "60% 40% 70% 30%/50% 60% 40% 50%", background: `radial-gradient(circle,${b.c} 0%,transparent 70%)`, opacity: .18, filter: "blur(40px)", animation: `blobDrift ${b.dur} ease-in-out ${b.del} infinite`, transform: "translate(-50%,-50%)" }} />
            ))}
          </div>
          {/* #1 Particles */}
          <div className="absolute inset-0 z-0 pointer-events-none" aria-hidden>
            {PARTICLES.map(p => (
              <div key={p.id} style={{ position: "absolute", left: p.left, top: p.top, width: p.size, height: p.size, borderRadius: "50%", backgroundColor: "#60a5fa", opacity: .5, animation: `particleRise ${p.dur}s linear ${p.delay}s infinite` }} />
            ))}
          </div>

          <div className="relative z-10 mx-auto max-w-7xl px-6 w-full text-white">
            <div className="max-w-4xl space-y-8">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="inline-flex items-center gap-2 px-3 py-1 rounded bg-primary/20 border border-primary/30 text-primary text-xs font-black uppercase tracking-[0.2em]"
              >
                Expertise Logistique Industrielle
              </motion.div>

              <h1 className="text-5xl md:text-7xl font-black leading-[1.1] tracking-tighter min-h-[2.2em]">
                Optimisation Intelligente de votre <br />
                <span className="text-primary inline-block relative">
                  <AnimatePresence mode="wait">
                    <motion.span
                      key={index}
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      exit={{ y: -20, opacity: 0 }}
                      transition={{ duration: 0.5, ease: "easeInOut" }}
                      className="inline-block"
                    >
                      {dynamicWords[index]}
                    </motion.span>
                  </AnimatePresence>
                </span>
              </h1>

              <p className="text-xl text-slate-300 max-w-2xl leading-relaxed font-medium">
                Prenez les meilleures décisions grâce à nos outils de simulation intelligente, trouvez l'emplacement idéal et garantissez la qualité avec notre suivi IoT en temps réel.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                {/* #4 Shimmer CTA */}
                <div className="relative overflow-hidden group flex-1 sm:flex-none">
                  <motion.div {...(rm ? {} : { whileHover: { scale: 1.05, y: -5 }, whileTap: { scale: .98 } })} className="flex-1 sm:flex-none">
                    <Button
                      onClick={() => setShowSimulationVideo(true)}
                      size="lg"
                      className="h-14 w-full px-8 text-lg font-black rounded-none shadow-xl transition-shadow hover:shadow-primary/40"
                    >
                      OPTISTOCK EN BREF <ArrowRight className="ml-3 h-5 w-5" />
                    </Button>
                  </motion.div>
                  {!rm && <span className="pointer-events-none absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/20 to-transparent" aria-hidden />}
                </div>
              </div>
            </div>
          </div>
        </section>
        {/* Wave hero→services */}
        <WaveSep dark />

        {/* Modules Section */}
        <RevealDiv>
          <section id="services" className="py-24 bg-slate-50 dark:bg-slate-900/50 scroll-mt-20">
            <div className="mx-auto max-w-7xl px-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                {/* Module Chercheur — #3 glassmorphism + hover glow */}
                <motion.div {...(rm ? {} : { whileHover: { y: -6 } })} transition={{ type: "spring", stiffness: 300, damping: 20 }} className="group backdrop-blur-sm bg-white dark:bg-slate-900 p-10 border border-slate-200/60 dark:border-white/10 shadow-sm hover:shadow-2xl hover:shadow-blue-500/20 hover:border-blue-400/40 transition-all flex flex-col justify-between">
                  <div>
                    <div className="h-14 w-14 bg-primary/10 text-primary flex items-center justify-center mb-8">
                      <Search className="h-8 w-8" />
                    </div>
                    <h2 className="text-3xl font-black mb-4 tracking-tight">Espace Client Logistique</h2>
                    <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed font-medium">
                      Optimisez votre chaîne logistique grâce à nos deux modules d'intelligence artificielle intégrés.
                    </p>
                  </div>
                  <ul className="space-y-4 mb-10">
                    {[
                      "MODULE 1 : Recherche d'emplacement optimal",
                      "MODULE 2 : Simulation & Optimization Lab",
                      "Réduction des temps de livraison",
                      "Réservation & Location directe"
                    ].map((item, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm font-bold">
                        <div className="h-1.5 w-1.5 bg-primary rounded-full" /> {item}
                      </li>
                    ))}
                  </ul>
                </motion.div>

                {/* Module Propriétaire — #3 glassmorphism + hover glow */}
                <motion.div {...(rm ? {} : { whileHover: { y: -6 } })} transition={{ type: "spring", stiffness: 300, damping: 20 }} className="group backdrop-blur-sm bg-white dark:bg-slate-900 p-10 border border-slate-200/60 dark:border-white/10 shadow-sm hover:shadow-2xl hover:shadow-blue-500/20 hover:border-blue-400/40 transition-all flex flex-col justify-between">
                  <div>
                    <div className="h-14 w-14 bg-blue-500/10 text-blue-500 flex items-center justify-center mb-8">
                      <Database className="h-8 w-8" />
                    </div>
                    <h2 className="text-3xl font-black mb-4 tracking-tight">Module Propriétaire</h2>
                    <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed font-medium">
                      Gérez vos actifs logistiques et prouvez votre qualité. Suivez en temps réel la <strong>température et l'humidité</strong>.
                    </p>
                  </div>
                  <ul className="space-y-4 mb-10">
                    {[
                      "Monitoring IoT Temps Réel",
                      "Alertes de conformité IoT",
                      "Gestion des offres de location",
                      "Historique des relevés capteurs"
                    ].map((item, i) => (
                      <li key={i} className="flex items-center gap-3 text-sm font-bold">
                        <div className="h-1.5 w-1.5 bg-blue-500 rounded-full" /> {item}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </div>
            </div>
          </section>
        </RevealDiv>

        {/* Wave services→tech */}
        <WaveSep dark={false} />

        {/* Technical Features */}
        <section id="tech" className="py-24 border-t border-slate-200 dark:border-slate-800 scroll-mt-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="flex flex-col md:flex-row justify-between items-center gap-12 mb-20">
              <div className="max-w-2xl">
                <h2 className="text-4xl font-black mb-6 tracking-tighter uppercase">La Technologie au Service de Votre Rentabilité</h2>
                <p className="text-lg text-slate-600 dark:text-slate-400 font-medium">
                  OptiStock transforme vos flux physiques en données décisionnelles grâce à son moteur d'optimisation intégré.
                </p>
              </div>
              <div className="flex gap-4">
                <div className="text-center p-6 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <p className="text-3xl font-black text-primary">24/7</p>
                  <p className="text-[10px] font-bold uppercase tracking-widest opacity-60">Suivi IoT</p>
                </div>
                <div className="text-center p-6 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                  <p className="text-3xl font-black text-primary">I.A.</p>
                  <p className="text-[10px] font-bold uppercase tracking-widest opacity-60">Smart Routing</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { title: "Conformité Logistique", desc: "Suivi rigoureux de l'environnement (température, humidité) et de la qualité de stockage.", icon: ShieldCheck },
                { title: "Stratégie d'Implantation", desc: "Analyse automatisée du positionnement idéal pour réduire vos coûts kilométriques.", icon: MapPin },
                { title: "Suivi en temps réel de IOT", desc: "Visualisation immédiate des capteurs pour une réactivité maximale.", icon: Thermometer }
              ].map((feat, i) => (
                <div key={i} className="flex gap-4">
                  <div className="h-10 w-10 shrink-0 bg-primary/10 text-primary flex items-center justify-center rounded">
                    <feat.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="font-black text-lg mb-2 uppercase tracking-tighter">{feat.title}</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">{feat.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section id="team" className="py-24 border-t border-slate-200 dark:border-slate-800 scroll-mt-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="text-center mb-16">
              <p className="text-sm font-bold text-primary tracking-widest uppercase mb-2">Expertise Logicielle</p>
              <h2 className="text-4xl font-black uppercase tracking-tighter">L'Équipe OptiStock</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {TEAM_GH.map((member, i) => (
                <motion.div key={i} {...(rm ? {} : { whileHover: { y: -6 } })} transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className="group backdrop-blur-sm bg-slate-50 dark:bg-slate-900 p-8 border border-slate-200/60 dark:border-white/10 text-center shadow-sm hover:shadow-xl hover:shadow-blue-500/20 hover:border-blue-400/40 transition-all flex flex-col items-center gap-3">
                  <Image src={`https://github.com/${member.gh}.png?size=120`} alt={member.name} width={96} height={96} className="rounded-full border-2 border-primary/20 group-hover:border-blue-400 transition-all" />
                  <h3 className="font-black text-xl">{member.name}</h3>
                  <p className="text-[10px] font-bold text-primary uppercase tracking-widest">{member.role}</p>
                  <a href={`https://github.com/${member.gh}`} target="_blank" rel="noopener noreferrer"
                    className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded border border-slate-200 dark:border-white/10 text-xs font-bold hover:bg-primary hover:text-white hover:border-primary transition-all">
                    <GHIcon /> GitHub
                  </a>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="py-24 bg-primary text-white">
          <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-10 text-center md:text-left">
            <div>
              <h2 className="text-4xl font-black tracking-tighter mb-4">Prêt à optimiser votre logistique ?</h2>
              <p className="text-lg font-medium opacity-90 uppercase tracking-widest text-xs">Innovation Industrielle OptiStock</p>
            </div>
            <motion.div whileHover={{ scale: 1.05, y: -2 }} whileTap={{ scale: 0.98 }} transition={{ type: "spring", stiffness: 400, damping: 25 }}>
              <Link href="/signup">
                <Button size="lg" className="bg-white text-primary hover:bg-slate-100 font-black px-10 h-14 rounded-none shadow-2xl">
                  COMMENCER
                </Button>
              </Link>
            </motion.div>
          </div>
        </section>
      </main>

      <footer className="bg-slate-950 text-slate-400 py-12 border-t border-white/10">
        <div className="mx-auto max-w-7xl px-6 flex flex-col items-center gap-6 text-center">
          {/* Email */}
          <a href="mailto:support.optistock@gmail.com"
            className="inline-flex items-center gap-2 text-sm hover:text-blue-400 hover:underline transition-colors">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-4 w-4" aria-hidden>
              <rect x="2" y="4" width="20" height="16" rx="2" />
              <path d="M2 7l10 7 10-7" />
            </svg>
            support.optistock@gmail.com
          </a>
          {/* GitHub links */}
          <div className="flex items-center gap-4">
            {TEAM_GH.map(m => (
              <a key={m.gh} href={`https://github.com/${m.gh}`} target="_blank" rel="noopener noreferrer"
                title={m.name} className="hover:text-blue-400 transition-colors">
                <GHIcon />
              </a>
            ))}
          </div>
          <div className="border-t border-white/10 w-full pt-6 space-y-1">
            <p className="text-[10px] font-bold uppercase tracking-[0.5em]">© 2026 OptiStock Solutions · ENSA Béni Mellal, TDI </p>
          </div>
        </div>
      </footer>

      {/* Simulation Video Modal */}
      <AnimatePresence>
        {showSimulationVideo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4"
            onClick={() => setShowSimulationVideo(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
              className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-none shadow-2xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header inside Modal */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                  <h3 className="font-black text-lg uppercase tracking-wider text-white">Démonstration de la Simulation OptiStock</h3>
                </div>
                <button
                  onClick={() => setShowSimulationVideo(false)}
                  className="text-slate-400 hover:text-white hover:rotate-90 transition-all duration-300 p-1"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>

              {/* Video Player */}
              <div className="relative aspect-video bg-black flex items-center justify-center">
                <video
                  src="/eliminer_les_texte_202605202350.mp4"
                  className="w-full h-full"
                  controls
                  autoPlay
                  loop
                  playsInline
                />
              </div>

              {/* Footer info in Modal */}
              <div className="bg-slate-950 px-6 py-4 border-t border-slate-800 text-xs text-slate-400 font-medium flex items-center justify-between">
                <p>Visualisation de l'algorithme d'optimisation de parc et recherche d'emplacement.</p>
                <Button
                  onClick={() => setShowSimulationVideo(false)}
                  variant="ghost"
                  className="text-xs font-black uppercase text-white hover:bg-white/10"
                >
                  Fermer
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
