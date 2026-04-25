"use client"

import { useEffect, useMemo, useState } from "react"
import { MapIcon, Clock, RefreshCcw, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { getActiveVisitors, HttpError } from "@/lib/api"
import { useSession } from "@/hooks/use-session"
import AccessDenied from "@/components/access-denied"

export default function VisitorTrackingPage() {
  const { loading: sessionLoading, authenticated, user } = useSession({ redirectToLogin: true })
  const [rawVisitors, setRawVisitors] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const unauthorized = !sessionLoading && authenticated && user?.role !== "admin"

  const fetchVisitors = async () => {
    try {
      const res = await getActiveVisitors()
      setRawVisitors(res.visitors || [])
      setError(null)
    } catch (e) {
      setError(e instanceof HttpError ? e.message : "Failed to load visitors")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (sessionLoading || !authenticated) return
    if (user?.role !== "admin") return

    fetchVisitors()
    
    // Set up polling every 5 seconds
    const interval = setInterval(fetchVisitors, 5000)
    
    return () => clearInterval(interval)
  }, [authenticated, sessionLoading, user?.role])

  const visitors = useMemo(() => {
    return (rawVisitors || []).map((v: any) => {
      const expectedExit = v.expectedExitTime || v.expected_exit_time
      let timeRemaining = ""
      if (expectedExit) {
        const end = new Date(expectedExit).getTime()
        const diff = end - Date.now()
        const mins = Math.floor(Math.abs(diff) / 60000)
        const secs = Math.floor((Math.abs(diff) % 60000) / 1000)
        const mm = String(mins).padStart(2, "0")
        const ss = String(secs).padStart(2, "0")
        timeRemaining = `${diff < 0 ? "-" : ""}${mm}:${ss}`
      }

      const compliance = Number(v.routeCompliance?.complianceScore ?? v.route_compliance?.compliance_score ?? 0)
      const progress = Number.isFinite(compliance) ? Math.max(0, Math.min(100, compliance)) : 0

      const destination = v.assignedRoute?.routeDescription || v.assigned_route?.route_description || ""

      return {
        id: v.visitorId || v.visitor_id || v.id,
        name: v.name || "Visitor",
        host: v.hostName || v.host_name || "",
        destination: destination || "",
        progress,
        timeRemaining: timeRemaining || "N/A",
        status: v.status || "active",
        photo: v.photo || "/placeholder.svg",
      }
    })
  }, [rawVisitors])

  if (unauthorized) {
    return <AccessDenied required={["admin"]} />
  }

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="h-16 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded bg-warning/10">
              <MapIcon className="w-5 h-5 text-warning" />
            </div>
            <span className="font-bold text-lg">LIVE TRACKING</span>
          </div>
          <Badge variant="outline" className="bg-warning/10 text-warning border-warning/20">
            {isLoading ? "..." : `${visitors.length} ACTIVE VISITORS`}
          </Badge>
          <Button variant="ghost" size="icon" onClick={fetchVisitors} disabled={isLoading} className="h-8 w-8 ml-2">
            <RefreshCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Main Map Area */}
        <main className="flex-1 relative bg-slate-950 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:40px_40px] opacity-20" />
          
          {/* Map Grid/Blueprint */}
          <div className="absolute inset-12 border-2 border-border/20 rounded-3xl overflow-hidden bg-card/5">
            <svg className="w-full h-full opacity-40" viewBox="0 0 1000 600">
              <rect x="100" y="100" width="200" height="150" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
              <text x="110" y="125" fill="currentColor" fontSize="12" className="font-mono">BUILDING A</text>
              
              <rect x="400" y="50" width="250" height="200" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
              <text x="410" y="75" fill="currentColor" fontSize="12" className="font-mono">MAIN LABS</text>
              
              <rect x="700" y="300" width="200" height="200" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
              <text x="710" y="325" fill="currentColor" fontSize="12" className="font-mono">FACULTY HUB</text>
              
              <circle cx="500" cy="500" r="100" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="5 5" />
              <text x="460" y="505" fill="currentColor" fontSize="12" className="font-mono">CENTRAL PLAZA</text>
            </svg>

            {/* Visitor Dots on Map */}
            {visitors.map((v, i) => {
              // Deterministic but "random" positions for demo
              const x = 150 + (parseInt(v.id.slice(0, 2), 16) % 700)
              const y = 100 + (parseInt(v.id.slice(2, 4), 16) % 400)
              
              return (
                <div 
                  key={`dot-${v.id}`}
                  className="absolute transition-all duration-1000 ease-in-out"
                  style={{ left: `${x}px`, top: `${y}px` }}
                >
                  <div className={`w-3 h-3 rounded-full animate-ping absolute ${v.status === 'Alert' ? 'bg-destructive' : 'bg-accent'}`} />
                  <div className={`w-3 h-3 rounded-full relative ${v.status === 'Alert' ? 'bg-destructive' : 'bg-accent'} border-2 border-white`} />
                  <div className="absolute top-4 left-1/2 -translate-x-1/2 whitespace-nowrap bg-black/80 px-2 py-0.5 rounded text-[10px] font-bold text-white">
                    {v.name}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Map Overlay Controls */}
          <div className="absolute bottom-6 left-6 flex items-center gap-3">
            <div className="bg-card/80 backdrop-blur-md p-3 rounded-xl border border-border flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-wider">System Online</span>
              </div>
              <div className="w-px h-4 bg-border" />
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-foreground uppercase">Signal Strength:</span>
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4].map(i => <div key={i} className="w-1 h-2 bg-accent rounded-full" />)}
                </div>
              </div>
            </div>
          </div>
        </main>

        <aside className="w-96 border-l border-border bg-card/30 backdrop-blur-sm flex flex-col shrink-0">
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-4">
              {error && (
                <div className="text-xs text-destructive border border-destructive/30 bg-destructive/10 rounded-md p-3">
                  {error}
                </div>
              )}
              {isLoading && visitors.length === 0 && (
                <div className="flex flex-col items-center justify-center h-32 space-y-2">
                  <RefreshCcw className="w-5 h-5 text-muted-foreground animate-spin" />
                  <p className="text-xs text-muted-foreground">Initializing tracking...</p>
                </div>
              )}
              {visitors.length === 0 && !isLoading && (
                <div className="flex flex-col items-center justify-center h-32 text-center">
                  <Users className="w-8 h-8 text-muted-foreground mb-2" />
                  <p className="text-xs text-muted-foreground">No active visitors currently on campus.</p>
                </div>
              )}
              {visitors.map((visitor) => (
                <Card
                  key={visitor.id}
                  className={`glass-card overflow-hidden transition-all hover:border-border/80 ${
                    visitor.status === "Alert" ? "border-destructive/50 bg-destructive/5" : ""
                  }`}
                >
                  <CardContent className="p-4 space-y-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="relative">
                          <img
                            src={visitor.photo || "/placeholder.svg"}
                            alt={visitor.name}
                            className="w-10 h-10 rounded-full border-2 border-border"
                          />
                          <div
                            className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-card ${
                              visitor.status === "Alert"
                                ? "bg-destructive"
                                : visitor.status === "Completed"
                                  ? "bg-success"
                                  : visitor.status === "Delayed"
                                    ? "bg-warning"
                                    : "bg-primary"
                            }`}
                          />
                        </div>
                        <div>
                          <h4 className="text-sm font-bold">{visitor.name}</h4>
                          <p className="text-[10px] text-muted-foreground uppercase">Host: {visitor.host}</p>
                        </div>
                      </div>
                      <Badge
                        variant={visitor.status === "Alert" ? "destructive" : "outline"}
                        className="text-[10px] h-5"
                      >
                        {visitor.status}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-[10px] font-bold uppercase">
                        <span className="text-muted-foreground">Route Progress</span>
                        <span>{visitor.progress}%</span>
                      </div>
                      <Progress
                        value={visitor.progress}
                        className="h-1"
                        indicatorClassName={
                          visitor.status === "Alert"
                            ? "bg-destructive"
                            : visitor.status === "Delayed"
                              ? "bg-warning"
                              : "bg-accent"
                        }
                      />
                    </div>

                    <div className="flex items-center justify-between text-[10px]">
                      <div className="flex items-center gap-1.5 text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        <span>Est. Remaining:</span>
                        <span
                          className={`font-mono font-bold ${visitor.timeRemaining.startsWith("-") ? "text-destructive" : "text-foreground"}`}
                        >
                          {visitor.timeRemaining}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-muted-foreground">
                        <MapIcon className="w-3 h-3" />
                        <span>
                          To: <span className="text-foreground">{visitor.destination}</span>
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </aside>
      </div>
    </div>
  )
}
