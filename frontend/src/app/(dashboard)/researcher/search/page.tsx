"use client"

import { useState } from "react"
import { SearchWizard } from "@/components/researcher/search-wizard"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Search } from "lucide-react"

export default function SearchPage() {
  // On garde l'état search par défaut et on retire la possibilité de changer
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div 
          className={cn(
            "flex-1 flex items-center gap-4 p-6 rounded-2xl border-2 transition-all text-left bg-primary/5 border-primary shadow-lg shadow-primary/10"
          )}
        >
          <div className="h-14 w-14 rounded-xl flex items-center justify-center bg-primary text-white">
            <Search className="h-7 w-7" />
          </div>
          <div>
            <h3 className="font-bold text-lg text-primary">Recherche & Classement Logistique</h3>
            <p className="text-sm text-muted-foreground font-medium">Trouver un entrepôt existant dans la base de données</p>
            <p className="text-[10px] text-muted-foreground/70 mt-1 uppercase tracking-wider font-bold underline decoration-primary/30 underline-offset-4">Module d'Analyse Opérationnelle</p>
          </div>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <SearchWizard />
      </motion.div>
    </div>
  )
}
