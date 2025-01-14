import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";

const attributes = [
  "Title", "Summary", "Affected Products", "Summary Details", 
  "Conformity Assessment", "Marking Requirement", "Technical Requirement",
  "Publish Date", "Effective Date", "Mandatory Date", "Consultation Closing"
];

export default function Index() {
  const [topic, setTopic] = useState("");
  const [url, setUrl] = useState("");
  const { toast } = useToast();

  const handleSubmit = () => {
    if (!topic || !url) {
      toast({
        title: "Validation Error",
        description: "Please enter both topic and URL",
        variant: "destructive",
      });
      return;
    }
    
    toast({
      title: "Processing",
      description: "Analyzing content...",
    });
  };

  const handleClear = () => {
    setTopic("");
    setUrl("");
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2">
          AI Assisted Research Tool
        </h1>
        <p className="text-muted-foreground">
          Analyze regulatory compliance with advanced AI
        </p>
      </div>

      {/* Input Section */}
      <Card className="glass-card mb-8">
        <CardHeader>
          <CardTitle>Research Parameters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Topic</label>
              <Input
                placeholder="Enter research topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="input-field"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">URL</label>
              <Input
                placeholder="Enter URL to analyze"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="input-field"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={handleClear}
              className="button-hover"
            >
              Clear
            </Button>
            <Button 
              onClick={handleSubmit}
              className="button-hover"
            >
              Analyze
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results Section */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={attributes[0]} className="w-full">
            <ScrollArea className="w-full mb-4">
              <TabsList className="w-full inline-flex flex-wrap justify-start gap-2 h-auto p-2">
                {attributes.map((attr) => (
                  <TabsTrigger
                    key={attr}
                    value={attr}
                    className="whitespace-nowrap"
                  >
                    {attr}
                  </TabsTrigger>
                ))}
              </TabsList>
            </ScrollArea>

            {attributes.map((attr) => (
              <TabsContent key={attr} value={attr} className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">{attr} Analysis</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">LLM Prompt</label>
                      <Textarea
                        placeholder="AI prompt will appear here"
                        className="h-24 input-field bg-muted/50"
                        readOnly
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">AI Generated Analysis</label>
                      <Textarea
                        placeholder="AI analysis will appear here"
                        className="h-32 input-field"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Expert Analysis</label>
                      <Textarea
                        placeholder="Expert analysis will appear here"
                        className="h-32 input-field"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Feedback</label>
                        <Input
                          placeholder="Enter feedback"
                          className="input-field"
                        />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Accuracy (%)</label>
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          placeholder="Enter accuracy"
                          className="input-field"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}