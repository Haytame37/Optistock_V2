"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SearchWizard } from "@/components/researcher/search-wizard"
import { WeberCalculator } from "@/components/researcher/weber-calculator"

export default function SearchPage() {
  return (
    <div className="space-y-6">
      <Tabs defaultValue="search" className="w-full">
        <TabsList className="w-full justify-start">
          <TabsTrigger value="search">Module 1: Trouver un entrepôt</TabsTrigger>
          <TabsTrigger value="weber">Module 2: Implanter un entrepôt</TabsTrigger>
        </TabsList>
        <TabsContent value="search">
          <SearchWizard />
        </TabsContent>
        <TabsContent value="weber">
          <WeberCalculator />
        </TabsContent>
      </Tabs>
    </div>
  )
}
