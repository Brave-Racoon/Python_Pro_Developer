package main

import (
	"compress/gzip"
	"encoding/csv"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath" // Added import
	"strconv"       // Added import
	"strings"       // Added import
	"sync"

	"github.com/bradfitz/gomemcache/memcache" // For Memcached interaction
	pb "homework_17/appsinstalled"            // Adjust this to your protobuf package
	"google.golang.org/protobuf/proto"        // Added import for protobuf
)

const NORMAL_ERR_RATE = 0.01

type AppsInstalled struct {
	DevType string
	DevID   string
	Lat     float64
	Lon     float64
	Apps    []uint32
}

type DeviceMemcache struct {
	IDFA string
	GAID string
	ADID string
	DVID string
}

func dotRename(path string) {
	head := filepath.Dir(path)
	fn := filepath.Base(path)
	if err := os.Rename(path, filepath.Join(head, "."+fn)); err != nil {
		log.Printf("Can't rename a file: %s", path)
	}
}

func processLine(line []string, deviceMemcache *DeviceMemcache) *AppsInstalled {
	if len(line) < 5 {
		return nil
	}
	devType, devID, latStr, lonStr, rawApps := line[0], line[1], line[2], line[3], line[4]
	if devType == "" || devID == "" {
		return nil
	}

	lat, lon, err := parseCoords(latStr, lonStr)
	if err != nil {
		log.Println("Invalid geo coords:", err)
		return nil
	}

	apps, err := parseApps(rawApps)
	if err != nil {
		log.Println("Not all user apps are digits:", err)
	}

	return &AppsInstalled{devType, devID, lat, lon, apps}
}

func parseCoords(latStr, lonStr string) (float64, float64, error) {
	var lat, lon float64
	var err error
	if lat, err = strconv.ParseFloat(latStr, 64); err != nil {
		return 0, 0, err
	}
	if lon, err = strconv.ParseFloat(lonStr, 64); err != nil {
		return 0, 0, err
	}
	return lat, lon, nil
}

func parseApps(rawApps string) ([]uint32, error) {
	raw := strings.Split(rawApps, ",")
	apps := make([]uint32, 0, len(raw))
	for _, app := range raw {
		if appNum, err := strconv.Atoi(strings.TrimSpace(app)); err == nil {
			apps = append(apps, uint32(appNum))
		}
	}
	return apps, nil
}

func insertAppsInstalled(memc *memcache.Client, appsInstalledList []*AppsInstalled, dryRun bool) bool {
	var items = make(map[string]*pb.UserApps)
	for _, appsInstalled := range appsInstalledList {
		ua := &pb.UserApps{
			Lat:  &appsInstalled.Lat, // Use pointers if needed
			Lon:  &appsInstalled.Lon, // Use pointers if needed
			Apps: appsInstalled.Apps,   // Ensure the type matches your Protobuf definition (i.e., []int32 vs. []uint32)
		}
		key := fmt.Sprintf("%s:%s", appsInstalled.DevType, appsInstalled.DevID)
		if dryRun {
			log.Printf("Dry run: %s - %v", key, ua)
			continue
		}
		items[key] = ua
	}
	
	if !dryRun {
		for key, ua := range items {
			packed, err := proto.Marshal(ua)
			if err != nil {
				log.Println("Cannot serialize UserApps:", err)
				return false
			}
			err = memc.Set(&memcache.Item{Key: key, Value: packed})
			if err != nil {
				log.Printf("Cannot write to memc: %v", err)
				return false
			}
		}
	}
	return true
}

func processFile(filePath string, deviceMemcache *DeviceMemcache, dryRun bool) {
	file, err := os.Open(filePath)
	if err != nil {
		log.Fatalf("Failed to open file: %v", err)
	}
	defer file.Close()

	gzipReader, err := gzip.NewReader(file)
	if err != nil {
		log.Fatalf("Failed to create gzip reader: %v", err)
	}
	defer gzipReader.Close()

	reader := csv.NewReader(gzipReader)
	reader.Comma = '\t' // Set the delimiter to tab
	lines, err := reader.ReadAll()
	if err != nil {
		log.Fatalf("Failed to read lines: %v", err)
	}

	memc := memcache.New(deviceMemcache.IDFA, deviceMemcache.GAID, deviceMemcache.ADID, deviceMemcache.DVID) // adjust as necessary
	appsInstalledList := make([]*AppsInstalled, 0)

	for _, line := range lines {
		if appsInstalled := processLine(line, deviceMemcache); appsInstalled != nil {
			appsInstalledList = append(appsInstalledList, appsInstalled)
		}
	}

	if insertAppsInstalled(memc, appsInstalledList, dryRun) {
		log.Printf("Processed %d entries successfully", len(appsInstalledList))
	} else {
		log.Printf("Failed to process %d entries", len(appsInstalledList))
	}
	
	//return appsInstalledList, nil
}

func main() {
	dryRun := flag.Bool("dry", false, "Dry run mode")
	pattern := flag.String("pattern", "/data/appsinstalled/*.tsv.gz", "Pattern for input files")
	idfa := flag.String("idfa", "127.0.0.1:33013", "Memcached address for IDFA")
	gaid := flag.String("gaid", "127.0.0.1:33014", "Memcached address for GAID")
	adid := flag.String("adid", "127.0.0.1:33015", "Memcached address for ADID")
	dvid := flag.String("dvid", "127.0.0.1:33016", "Memcached address for DVID")
	flag.Parse()

	deviceMemcache := &DeviceMemcache{*idfa, *gaid, *adid, *dvid}
	var wg sync.WaitGroup

	// Retrieve the files matching the pattern and process them
	files, _ := filepath.Glob(*pattern) // Use filepath and glob pattern matching
	for _, filePath := range files {
		wg.Add(1)
		go func(filePath string) {
			defer wg.Done()

			// Process the file
			processFile(filePath, deviceMemcache, *dryRun)
			// Rename the file after processing is completed
			dotRename(filePath)
			

		}(filePath)
	}

	wg.Wait()
	log.Println("Finished processing files")
}