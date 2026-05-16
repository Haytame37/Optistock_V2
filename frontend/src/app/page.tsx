"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/layout/theme-toggle"
import { motion, AnimatePresence } from "framer-motion"
import { 
  ArrowRight, 
  MapPin, 
  Package, 
  Search, 
  ShieldCheck, 
  TrendingUp, 
  Database,
  Thermometer,
  ChevronRight
} from "lucide-react"

const dynamicWords = [
  "Réseau de Stockage",
  "Chaîne Logistique",
  "Implantation Industrielle",
  "Monitoring IoT"
]

export default function LandingPage() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % dynamicWords.length)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
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
              <button onClick={() => scrollToSection('services')} className="hover:text-primary transition-colors">Nos Services</button>
              <button onClick={() => scrollToSection('tech')} className="hover:text-primary transition-colors">La Technologie au Service de Votre Rentabilité</button>
              <button onClick={() => scrollToSection('team')} className="hover:text-primary transition-colors">L'Équipe</button>
            </nav>
            <div className="h-6 w-px bg-slate-200 dark:bg-slate-800 hidden md:block" />
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost" className="font-bold">CONNEXION</Button>
            </Link>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Link href="/signup">
                <Button className="font-bold px-6">DÉMARRER</Button>
              </Link>
            </motion.div>
          </div>
        </div>
      </header>

      <main>
        {/* Hero Section */}
        <section className="relative h-[85vh] flex items-center overflow-hidden">
          <div className="absolute inset-0 z-0">
             <img 
               src="/modern_smart_warehouse_dashboard_1778782292438.png" 
               alt="Warehouse" 
               className="w-full h-full object-cover"
             />
             <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-transparent" />
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
                <motion.div whileHover={{ scale: 1.05, y: -5 }} whileTap={{ scale: 0.98 }} className="flex-1 sm:flex-none">
                  <Link href="/signup">
                    <Button size="lg" className="h-14 w-full px-8 text-lg font-black rounded-none shadow-xl transition-shadow hover:shadow-primary/40">
                      LANCER UNE SIMULATION <ArrowRight className="ml-3 h-5 w-5" />
                    </Button>
                  </Link>
                </motion.div>

              </div>
            </div>
          </div>
        </section>

        {/* Modules Section */}
        <section id="services" className="py-24 bg-slate-50 dark:bg-slate-900/50 scroll-mt-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              {/* Module Chercheur */}
              <div className="group bg-white dark:bg-slate-900 p-10 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-2xl hover:border-primary/50 transition-all">
                 <div className="h-14 w-14 bg-primary/10 text-primary flex items-center justify-center mb-8">
                    <Search className="h-8 w-8" />
                 </div>
                 <h2 className="text-3xl font-black mb-4 tracking-tight">Espace Chercheur</h2>
                 <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed font-medium">
                    Optimisez votre chaîne logistique grâce à nos deux modules d'intelligence artificielle intégrés.
                 </p>
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
                 <motion.div whileHover={{ x: 10 }} transition={{ type: "spring", stiffness: 400 }}>
                   <Link href="/signup">
                      <Button variant="link" className="p-0 text-primary font-black group-hover:gap-3 transition-all">
                         ACCÉDER AU MODULE <ChevronRight className="h-4 w-4" />
                      </Button>
                   </Link>
                 </motion.div>
              </div>

              {/* Module Propriétaire */}
              <div className="group bg-white dark:bg-slate-900 p-10 border border-slate-200 dark:border-slate-800 shadow-sm hover:shadow-2xl hover:border-primary/50 transition-all">
                 <div className="h-14 w-14 bg-blue-500/10 text-blue-500 flex items-center justify-center mb-8">
                    <Database className="h-8 w-8" />
                 </div>
                 <h2 className="text-3xl font-black mb-4 tracking-tight">Module Propriétaire</h2>
                 <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed font-medium">
                    Gérez vos actifs logistiques et prouvez votre qualité. Suivez en temps réel la <strong>température et l'humidité</strong>.
                 </p>
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
                 <motion.div whileHover={{ x: 10 }} transition={{ type: "spring", stiffness: 400 }}>
                   <Link href="/signup">
                      <Button variant="link" className="p-0 text-blue-500 font-black group-hover:gap-3 transition-all">
                         ACCÉDER AU MODULE <ChevronRight className="h-4 w-4" />
                      </Button>
                   </Link>
                 </motion.div>
              </div>
            </div>
          </div>
        </section>

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
                   { title: "IoT Live Tracking", desc: "Visualisation immédiate des capteurs pour une réactivité maximale.", icon: Thermometer }
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
                 {[
                   { name: "Atmane Salah", role: "Lead Data & Logistique" },
                   { name: "Rafiki Najat", role: "Responsable UX/UI & Auth" },
                   { name: "ElAtraoui Haytame", role: "Architecte API & Optimisation" }
                 ].map((member, i) => (
                    <div key={i} className="group p-8 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center hover:border-primary transition-all">
                       <div className="h-20 w-20 rounded-lg bg-primary/10 text-primary text-2xl font-black mx-auto flex items-center justify-center mb-6 group-hover:bg-primary group-hover:text-white transition-all">
                          {member.name.split(" ")[0][0]}
                       </div>
                       <h3 className="font-black text-xl mb-1">{member.name}</h3>
                       <p className="text-[10px] font-bold text-primary uppercase tracking-widest">{member.role}</p>
                    </div>
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
                       COMMENCER MAINTENANT
                    </Button>
                 </Link>
              </motion.div>
           </div>
        </section>
      </main>

      <footer className="py-12 border-t border-slate-200 dark:border-slate-800 text-center opacity-50">
         <p className="text-[10px] font-bold uppercase tracking-[0.5em]">© 2026 OptiStock · Industrial Logistics Engineering</p>
      </footer>
    </div>
  )
}
