"use client"

import { useState } from "react"
import { SearchWizard } from "@/components/researcher/search-wizard"
import { WeberCalculator } from "@/components/researcher/weber-calculator"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Search, MapPin } from "lucide-react"

export default function SearchPage() {
  const [activeTab, setActiveTab] = useState("search")
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <button 
          onClick={() => setActiveTab("search")}
          className={cn(
            "flex-1 flex items-center gap-4 p-6 rounded-2xl border-2 transition-all text-left group",
            activeTab === "search" 
              ? "bg-primary/5 border-primary shadow-lg shadow-primary/10" 
              : "bg-background border-transparent hover:border-primary/30 hover:bg-muted/50"
          )}
        >
          <div className={cn(
            "h-14 w-14 rounded-xl flex items-center justify-center transition-colors",
            activeTab === "search" ? "bg-primary text-white" : "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary"
          )}>
            <Search className="h-7 w-7" />
          </div>
          <div>
            <h3 className={cn("font-bold text-lg", activeTab === "search" ? "text-primary" : "text-foreground")}>Module 1</h3>
            <p className="text-sm text-muted-foreground font-medium">Recherche & Classement Logistique</p>
            <p className="text-[10px] text-muted-foreground/70 mt-1 uppercase tracking-wider font-bold">Trouver un entrepôt existant</p>
          </div>
        </button>

        <button 
          onClick={() => setActiveTab("weber")}
          className={cn(
            "flex-1 flex items-center gap-4 p-6 rounded-2xl border-2 transition-all text-left group",
            activeTab === "weber" 
              ? "bg-amber-500/5 border-amber-500 shadow-lg shadow-amber-500/10" 
              : "bg-background border-transparent hover:border-amber-500/30 hover:bg-muted/50"
          )}
        >
          <div className={cn(
            "h-14 w-14 rounded-xl flex items-center justify-center transition-colors",
            activeTab === "weber" ? "bg-amber-500 text-white" : "bg-muted text-muted-foreground group-hover:bg-amber-500/10 group-hover:text-amber-500"
          )}>
            <MapPin className="h-7 w-7" />
          </div>
          <div>
            <h3 className={cn("font-bold text-lg", activeTab === "weber" ? "text-amber-600" : "text-foreground")}>Module 2</h3>
            <p className="text-sm text-muted-foreground font-medium">Modèle de Gravité (Weber)</p>
            <p className="text-[10px] text-muted-foreground/70 mt-1 uppercase tracking-wider font-bold">Calcul d'implantation optimale</p>
          </div>
        </button>
      </div>

      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === "search" ? <SearchWizard /> : <WeberCalculator />}
      </motion.div>
    </div>
  )
}
