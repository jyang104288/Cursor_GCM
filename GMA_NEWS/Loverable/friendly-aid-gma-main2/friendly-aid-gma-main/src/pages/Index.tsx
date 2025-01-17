import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Save } from "lucide-react";
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';

const attributes = [
  "Title", "Summary", "Affected Products", "Summary Details", 
  "Conformity Assessment", "Marking Requirement", "Technical Requirement",
  "Publish Date", "Effective Date", "Mandatory Date", "Consultation Closing"
];

export default function Index() {
  const [topic, setTopic] = useState("");
  const [url, setUrl] = useState("");
  const [analysisResults, setAnalysisResults] = useState({});
  const [expertAnalysis, setExpertAnalysis] = useState({});
  const [feedback, setFeedback] = useState({});
  const [accuracy, setAccuracy] = useState({});
  const { toast } = useToast();

  const handleSubmit = async () => {
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

    try {
      const response = await fetch("http://127.0.0.1:5000/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic, url }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setAnalysisResults(data);
    } catch (error) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleClear = () => {
    setTopic("");
    setUrl("");
    setAnalysisResults({});
  };

  const handleSave = () => {
    const fileName = prompt("Please enter the file name:", "analysis_results.xlsx");
    if (!fileName) {
      toast({
        title: "Error",
        description: "File name is required.",
        variant: "destructive",
      });
      return; // Exit if no file name is provided
    }

    // Prepare data for the Excel file
    const data = attributes.map(attr => ({
      Attribute: attr,
      Prompt: analysisResults[attr]?.prompt || '',
      AI_Output: analysisResults[attr]?.ai_output || '',
      Expert_Analysis: expertAnalysis[attr] || '',
      Feedback: feedback[attr] || '',
      Accuracy: accuracy[attr] || '',
    }));

    // Create a new workbook and a worksheet
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Analysis Results');

    // Generate buffer and save the file
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });
    saveAs(blob, fileName); // Save the file with the user-defined name

    toast({
      title: "Success",
      description: `Analysis results saved successfully as ${fileName}.`,
    });
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
      <Card className="glass-card mb-8">
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
                        value={analysisResults[attr]?.prompt || ""}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">AI Generated Analysis</label>
                      <Textarea
                        placeholder="AI analysis will appear here"
                        className="h-32 input-field"
                        value={analysisResults[attr]?.ai_output || ""}
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Expert Analysis for {attr}</label>
                      <Textarea
                        placeholder="Enter expert analysis"
                        value={expertAnalysis[attr] || ''}
                        onChange={(e) => setExpertAnalysis({ ...expertAnalysis, [attr]: e.target.value })}
                        className="h-32 input-field"
                      />
                      <label className="text-sm font-medium">Feedback</label>
                      <Input
                        placeholder="Enter feedback"
                        value={feedback[attr] || ''}
                        onChange={(e) => setFeedback({ ...feedback, [attr]: e.target.value })}
                        className="input-field"
                      />
                      <label className="text-sm font-medium">Accuracy (%)</label>
                      <Input
                        type="number"
                        min="0"
                        max="100"
                        placeholder="Enter accuracy"
                        value={accuracy[attr] || ''}
                        onChange={(e) => setAccuracy({ ...accuracy, [attr]: e.target.value })}
                        className="input-field"
                      />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          className="button-hover"
          variant="default"
        >
          <Save className="mr-2" />
          Save Results
        </Button>
      </div>
    </div>
  );
}