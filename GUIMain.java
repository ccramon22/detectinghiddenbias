package pageRankGUI;
import javafx.application.Application;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.Stage;

import java.io.File;
import java.util.List;
import java.util.Map;

public class GUIMain extends Application {

    private File eventsFile;
    private File categoryFile;
    private TextArea outputArea;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("PageRank File Reader");
        
        Text eventchooser = new Text("Please choose an appropriate item catalog CSV file: ");
        Text treechooser = new Text("Please choose the matching category tree CSV file: ");

        Button loadEventsBtn = new Button("My Events CSV");
        Button loadCategoryBtn = new Button("My Category CSV");
        Button runBtn = new Button("Run PageRank");

        outputArea = new TextArea();
        outputArea.setEditable(false);

        loadEventsBtn.setOnAction(e -> eventsFile = chooseCSV(primaryStage));
        loadCategoryBtn.setOnAction(e -> categoryFile = chooseCSV(primaryStage));
        runBtn.setOnAction(e -> runPageRank());

        VBox root = new VBox(10, eventchooser, loadEventsBtn, treechooser, loadCategoryBtn, runBtn, outputArea);
        root.setPrefSize(600, 400);

        primaryStage.setScene(new Scene(root));
        primaryStage.show();
    }
    
    private File chooseCSV(Stage stage) {
        FileChooser chooser = new FileChooser();
        chooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("CSV Files", "*.csv")
        );
        return chooser.showOpenDialog(stage);
    }
    
    private void runPageRank() {
        if (eventsFile == null || categoryFile == null) {
            outputArea.setText("Please load both CSV files first.");
            return;
        }

        try {
            Map<Long, List<Event>> userEvents =
                    EventsReader.readEvents(eventsFile.getAbsolutePath());

            List<List<Long>> sessions =
                    SessionBuild.buildSessions(userEvents);

            Map<Long, Map<Long, Integer>> transitions =
                    TransitionMatrixBuild.buildTransitions(sessions);

            Map<Long, Map<Long, Double>> probMatrix =
                    ProbabilityMatrixBuild.normalize(transitions);

            Map<Long, Double> ranks =
                    PageRank.compute(probMatrix, 30, 0.99);

            Map<Long, Long> itemToParent =
                    CategoryReader.readCategoryTree(categoryFile.getAbsolutePath());

            StringBuilder sb = new StringBuilder();

            ranks.entrySet().stream()
                    .sorted((a, b) -> Double.compare(b.getValue(), a.getValue()))
                    .limit(100)
                    .forEach(entry -> {
                        long itemId = entry.getKey();
                        double score = entry.getValue();
                        Long parentId = itemToParent.get(itemId);

                        if (parentId != null)
                            sb.append(itemId).append(",")
                              .append(parentId).append(",")
                              .append(score).append("\n");
                        else
                            sb.append(itemId).append(",")
                              .append(score).append("\n");
                    });

            outputArea.setText(sb.toString());

        } catch (Exception ex) {
            outputArea.setText("Error:\n" + ex.getMessage());
            ex.printStackTrace();
        }
    } 
}