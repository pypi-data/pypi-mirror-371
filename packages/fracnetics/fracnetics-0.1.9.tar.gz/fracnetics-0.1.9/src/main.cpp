#include "../include/Data.hpp"
#include "../include/Population.hpp"
#include "../include/PrintHelper.hpp"
#include <chrono>

int main(){
    /**
     * Parameter
     */
    float probEdgeMutationStartNode = 0.03;
    float probEdgeMutationInnerNodes = 0.03;
    float probBoundaryMutation = 0.1;
    float sigmaBoundaryMutationNormal = 0.01;
    std::string boundaryMutationType = "normal"; // uniform, networkSigma, normal, edgeSigma, edgeFractal
    bool fractalJudgment = false;
    float probCrossOver = 0.05;
    int generations = 1000;
    int generationsNoImprovementLimit = 500;
    int nIndividuals = 300;
    int tournamentSize = 2;
    int nElite = 1;
    int jn = 1;
    int jnf = 4;
    int pn = 2;
    int pnf = 2;
    int dMax = 10;
    int penalty = 2;
    int maxConsecutiveP = 2;
    int addDel = 1;

    auto start = std::chrono::high_resolution_clock::now();
    /**
     * Initializing the population
     */
    Population population(
            123, // seed 
            nIndividuals, // number of networks
            jn, // number of judgment nodes (jn)
            jnf, // number of jn functions 
            pn, // number of processing nodes (pn)
            pnf, // number of pn functions
            fractalJudgment
            ); 
    
    std::vector<float> bestFitnessPerGeneration;
    int improvementCounter = 0;
    for(int g=0; g<generations; g++){
        //generator = std::make_shared<std::mt19937_64>(5494+g);
        population.callFitness(data.X, data.y, dMax, penalty, "cartpole", maxConsecutiveP);
        population.tournamentSelection(tournamentSize,nElite);
        population.callEdgeMutation(probEdgeMutationInnerNodes, probEdgeMutationStartNode);

        std::function<void(Node&, const Population::mutationBoundaryParam&)> boundaryMutation;
        if(boundaryMutationType == "normal"){
            boundaryMutation = [&](Node& node, const Population::mutationBoundaryParam& param) {
                    population.callBoundaryMutationNormal(node, param);
            };
         }else if(boundaryMutationType == "uniform"){
            boundaryMutation = [&](Node& node, const Population::mutationBoundaryParam& param) {
                    population.callBoundaryMutationUniform(node, param);
            };
        }else if(boundaryMutationType == "networkSigma"){
            boundaryMutation = [&](Node& node, const Population::mutationBoundaryParam& param) {
                    population.callBoundaryMutationNetworkSizeDependingSigma(node, param);
            };
        }else if (boundaryMutationType == "edgeSigma") {
             boundaryMutation = [&](Node& node, const Population::mutationBoundaryParam& param) {
                    population.callBoundaryMutationEdgeSizeDependingSigma(node, param);
            };
         }else if (boundaryMutationType == "edgeFractal") {
             boundaryMutation = [&](Node& node, const Population::mutationBoundaryParam& param) {
                    population.callBoundaryMutationFractal(node, param);
            };
        }
        
        population.applyBoundaryMutation(
                {probBoundaryMutation, sigmaBoundaryMutationNormal, 0, data.minX, data.maxX}, boundaryMutation
        );

        population.crossover(probCrossOver);
        if(addDel == 1){
            population.callAddDelNodes(data.minX, data.maxX, "fractal"); //TODO change type!!
        }
        std::cout << 
            "Geneation: " << g << 
            " BestFit: " << population.individuals[population.indicesElite[0]].fitness << 
            " MeanFitness: " << population.meanFitness << 
            " MinFitness: " << population.minFitness <<
            " NetworkSize Best Ind: " << population.individuals[population.indicesElite[0]].innerNodes.size() << std::endl;

        //std::cout << "Best Fit: " << population.individuals[population.indicesElite[0]].fitness;
        
        /*
        for(auto bestIndices : population.indicesElite){
            std::cout << "indicesElite: " << bestIndices;
        }
        std::cout << std::endl;
        
        for(int i=0; i<population.individuals.size(); i++){
            auto& net = population.individuals[i];
            printLine(); 
            std::cout << "Generation: " << g << " Network: " << i << " Fit: " << net.fitness << std::endl;
            printLine(); 
            std::cout << "type: " << net.startNode.type << " id: " << net.startNode.id << " edges: " << net.startNode.edges[0] << std::endl;
            for(const auto& n : net.innerNodes){
                std::cout << "type: " << n.type << " id: " << n.id << " F: " << n.f << " ";
                std::cout << "edges " << "(" << n.edges.size() << "): ";
                for(auto& ed : n.edges){
                    std::cout << ed << " ";
                }

                std::cout << "boundaries" << "(" << n.boundaries.size() << "): ";
                for(auto& b: n.boundaries){
                    std::cout << b << " ";
                }
                std::cout << std::endl;
            }
        }
        */
       bestFitnessPerGeneration.push_back(population.bestFit);
       if(g > 1 && bestFitnessPerGeneration[g-1] == bestFitnessPerGeneration[g]){
           improvementCounter++;
           if(improvementCounter == generationsNoImprovementLimit){
               break;
            }
        } else {
            improvementCounter = 0;
        }
    }
    auto& net = population.individuals[population.individuals.size()-1];
    printLine(); 
    std::cout << "Best Network: " << " Fit: " << net.fitness << std::endl;
    printLine(); 
    printLine(); 
    std::cout << "type: " << net.startNode.type << " id: " << net.startNode.id << " edge: " << net.startNode.edges[0] << std::endl;
    int nodeCounter = 0;
    for(const auto& n : net.innerNodes){
        std::string usedNodeMarker;
        if(std::find(net.usedNodes.begin(), net.usedNodes.end(), nodeCounter) == net.usedNodes.end()){
            usedNodeMarker = "";
        }else{
            usedNodeMarker = "*";
        }
        nodeCounter ++;
        std::cout << usedNodeMarker << "type: " << n.type << " id: " << n.id << " F: " << n.f << " k: " << n.k_d.first << " d: " << n.k_d.second << " ";
        std::cout << "edges " << "(" << n.edges.size() << "): ";
        for(auto& ed : n.edges){
            std::cout << ed << " ";
        }

        std::cout << "boundaries" << "(" << n.boundaries.size() << "): ";
        for(auto& b: n.boundaries){
            std::cout << b << " ";
        }
        std::cout << "Frac Parameter: ";
        for(auto& p: n.productionRuleParameter){
            std::cout << p << " ";
        }
        std::cout << std::endl;
    }
    printLine();
    //printVec(bestFitnessPerGeneration,"Best Fitness Values");
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration = end - start;
    std::cout << "done in:" << duration.count() << "sek. \n"; 
    
    int sumTestFitness = 0;
    int tests = 100;
    printLine();
    std::cout << "Validation" << std::endl;
    for(int t=0; t<tests; t++){
        //generator = std::make_shared<std::mt19937_64>(54+t);
        population.callFitness(data.dt, data.yIndices, data.XIndices, dMax, penalty, "cartpole", maxConsecutiveP);
        //std::cout << "Best Network: " << " Fit: " << population.individuals[population.indicesElite[0]].fitness << std::endl;
        sumTestFitness += population.individuals[population.indicesElite[0]].fitness; 
    }
    std::cout << "Mean Test Results: " << sumTestFitness/tests << std::endl;

    return 0;
}
