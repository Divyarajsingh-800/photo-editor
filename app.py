import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { motion } from "framer-motion";

const SentimentAnalyzer = () => {
  const [text, setText] = useState("");
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeSentiment = async () => {
    setLoading(true);
    // Dummy sentiment analysis logic
    const lowerText = text.toLowerCase();
    let result;
    if (lowerText.includes("good") || lowerText.includes("happy") || lowerText.includes("great")) {
      result = "Positive";
    } else if (lowerText.includes("bad") || lowerText.includes("sad") || lowerText.includes("terrible")) {
      result = "Negative";
    } else {
      result = "Neutral";
    }
    setTimeout(() => {
      setSentiment(result);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between items-center p-4 bg-gradient-to-br from-indigo-100 to-purple-200">
      <div className="w-full max-w-xl">
        <motion.h1
          className="text-4xl font-bold text-center text-indigo-800 mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Real-Time Sentiment Analyzer
        </motion.h1>
        <Card className="shadow-xl rounded-2xl">
          <CardContent className="p-6 space-y-4">
            <Input
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text to analyze..."
              className="rounded-xl"
            />
            <Button onClick={analyzeSentiment} disabled={loading} className="w-full rounded-xl">
              {loading ? "Analyzing..." : "Analyze Sentiment"}
            </Button>
            {sentiment && (
              <motion.div
                className={`text-xl font-semibold text-center mt-4 ${
                  sentiment === "Positive"
                    ? "text-green-600"
                    : sentiment === "Negative"
                    ? "text-red-600"
                    : "text-yellow-600"
                }`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                Sentiment: {sentiment}
              </motion.div>
            )}
          </CardContent>
        </Card>
      </div>
      <footer className="text-center text-sm text-gray-600 mt-10">
        DEVELOPED BY DIVYA RAJ SINGH
      </footer>
    </div>
  );
};

export default SentimentAnalyzer;
