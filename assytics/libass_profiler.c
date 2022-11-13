#include <stdio.h>
#include <time.h>
#include <libass/ass.h>

char* defaultoutputfile = "output.csv";
float fps = 23.976;

void printhelp() {
  printf("Usage: libass_profiler <assfile> <output>\n");
  printf("output is optional and defaults to %s\n",defaultoutputfile);
}

int timecode_string(char* output, long long ms_long){
  int cs = (ms_long % 1000) / 10;
  int s = (ms_long % 60000) / 1000;
  int m = (ms_long % 3600000) / 60000;
  int h = ms_long / 3600000;
  return sprintf(output,"%01d:%02d:%02d.%02d",h,m,s,cs);
}

long long find_track_duration_in_ms(ASS_Track* track){
  long long retval = 0;
  for (int i =0; i < track->n_events; i++){
    ASS_Event event = track->events[i];
    long long event_endtime = event.Start + event.Duration;
    retval = retval > event_endtime ? retval : event_endtime;
  }
  return retval;
}

int main(int argc, char *argv[]) {
  int version = ass_library_version();
  printf("libass version %d\n",version);
  if (argc < 2){
    printhelp();
    return 0;
  }
  char* inputfilename = argv[1];
  char* outputfilename = defaultoutputfile;
  if (argc > 3){
    outputfilename = argv[2];
  }
  ASS_Library* my_ass_library = ass_library_init();
  ass_set_extract_fonts(my_ass_library,1);
  ASS_Track* my_ass_track = ass_read_file(my_ass_library,inputfilename,NULL);
  ASS_Renderer* my_ass_renderer = ass_renderer_init(my_ass_library);
  ass_set_frame_size(my_ass_renderer, my_ass_track->PlayResX, my_ass_track->PlayResY);
  ass_set_fonts(my_ass_renderer,NULL,"Sans",1,NULL,1);
  long long track_duration = find_track_duration_in_ms(my_ass_track);

  FILE* outfile = fopen(outputfilename,"w");
  fprintf(outfile, "%s\n", inputfilename);
  fprintf(outfile, "time,total_image_size,largest_image_size,image_count,time_benchmark\n");
  for (long long t = 0; t < track_duration; t = t + 1000/fps) {
    long long frame_total_image_size = 0;
    long long frame_largest_image_size = 0;
    long long frame_image_count = 0;
    clock_t begin = clock();
    ASS_Image* my_ass_images = ass_render_frame(my_ass_renderer,my_ass_track,t,NULL);
    double frame_time_benchmark = (double)(clock() - begin) / CLOCKS_PER_SEC;
    while(my_ass_images != NULL){
      int h = my_ass_images->h;
      int w = my_ass_images->w;
      int stride = my_ass_images->stride;
      long long image_size = stride*(h-1) + w;
      frame_total_image_size += image_size;
      frame_largest_image_size = frame_largest_image_size > image_size ? frame_largest_image_size : image_size;
      frame_image_count++;
      my_ass_images = my_ass_images->next;
    }
    //write to stats
    char timecode[40];
    timecode_string(timecode, t);
    fprintf(outfile, "%s,%lld,%lld,%lld,%lf\n", timecode,frame_total_image_size,frame_largest_image_size,frame_image_count,frame_time_benchmark);
  }
  fclose(outfile);
  return 0;
}
