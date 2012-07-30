//
//  MMViewController.m
//  MagicMirror
//
//  Created by Doug Feigelson on 7/21/12.
//  Copyright (c) 2012 MIT. All rights reserved.
//

#import "MMViewController.h"
#import <RestKit/RestKit.h>
#import <AVFoundation/AVFoundation.h>
#import <RestKit/RKJSONParserJSONKit.h>

#define DOCUMENTS_FOLDER [NSHomeDirectory() stringByAppendingPathComponent:@"Documents"]

static int RECORDING_PERIOD = 6;
    
@interface MMViewController ()

@end

@implementation MMViewController
@synthesize recorder,webView,scrollView,contentMode,replacementWebView;

- (void)viewDidLoad
{
    [super viewDidLoad];
    
    // Setup the webview and scrollview
    contentMode = @"Web";
    
    scrollView = [[UIScrollView alloc] initWithFrame:CGRectMake(0, 0, 1024, 768)];
    scrollView.contentSize = CGSizeMake(1024*5, 768);
    scrollView.pagingEnabled = YES;
    scrollView.backgroundColor = [UIColor blackColor];
    scrollView.delegate = self;
    scrollView.showsHorizontalScrollIndicator = NO;
    [scrollView setBounces:NO];
    [self.view addSubview:scrollView];
    modes = [NSArray arrayWithObjects:@"Web",@"Image",@"Wikipedia",@"Analytical",@"Smart Select", nil];
    for (int i=0;i<5;i++) {
        UIImageView* iv = [[UIImageView alloc] initWithImage:[UIImage imageNamed:[NSString stringWithFormat:@"%@.png",[modes objectAtIndex:i]]]]; 
        iv.frame = CGRectMake((1024-350)/2+1024*i, (768-350)/2, 350, 350);
        [scrollView addSubview:iv];
        
//        UILabel* l = [[UILabel alloc] initWithFrame:CGRectMake((1024-300)/2+1024*i, (768-60)/2, 300, 60)];
//        l.font = [UIFont fontWithName:@"Arial" size:50];
//        l.textColor = [UIColor whiteColor];
//        l.backgroundColor = [UIColor clearColor];
//        [scrollView addSubview:l];
//        l.text = [modes objectAtIndex:i];
    }
    
    webView = nil;
    
    AVAudioSession *audioSession = [AVAudioSession sharedInstance];
    NSError *err = nil;
    [audioSession setCategory :AVAudioSessionCategoryPlayAndRecord error:&err];
    if(err){
        NSLog(@"audioSession: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        return;
    }
    [audioSession setActive:YES error:&err];
    err = nil;
    if(err){
        NSLog(@"audioSession: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        return;
    }
    
    BOOL audioHWAvailable = audioSession.inputIsAvailable;
    if (! audioHWAvailable) {
        UIAlertView *cantRecordAlert =
        [[UIAlertView alloc] initWithTitle: @"Warning"
                                   message: @"Audio input hardware not available"
                                  delegate: nil
                         cancelButtonTitle:@"OK"
                         otherButtonTitles:nil];
        [cantRecordAlert show];
        return;
    }
    
    [self makeNewRecorderAndRecord];
}

-(void) makeNewRecorderAndRecord {
    NSDictionary *recordSettings = [NSDictionary dictionaryWithObjectsAndKeys:
                                    [NSNumber numberWithInt:AVAudioQualityMedium],AVEncoderAudioQualityKey,
                                    [NSNumber numberWithInt:16], AVEncoderBitRateKey,
                                    [NSNumber numberWithInt: 2], AVNumberOfChannelsKey,
                                    [NSNumber numberWithFloat:16000.0], AVSampleRateKey,
                                    nil];
    
    
    // Create a new dated file
    NSDate *now = [NSDate dateWithTimeIntervalSinceNow:0];
    NSString *caldate = [now description];
    recordingFilePath = [NSString stringWithFormat:@"%@/%@.caf", DOCUMENTS_FOLDER, caldate];
    NSURL *url = [NSURL fileURLWithPath:recordingFilePath];
    NSError* err = nil;
    recorder = [[ AVAudioRecorder alloc] initWithURL:url settings:recordSettings error:&err];
    if(!recorder){
        NSLog(@"recorder: %@ %d %@", [err domain], [err code], [[err userInfo] description]);
        UIAlertView *alert =
        [[UIAlertView alloc] initWithTitle: @"Warning"
                                   message: [err localizedDescription]
                                  delegate: nil
                         cancelButtonTitle:@"OK"
                         otherButtonTitles:nil];
        [alert show];
        return;
    }
    
    //prepare to record
    [recorder setDelegate:self];
    [recorder prepareToRecord];
//    recorder.meteringEnabled = YES;
    
    // start recording
    [recorder recordForDuration:(NSTimeInterval) RECORDING_PERIOD];
}


-(void) audioRecorderDidFinishRecording:(AVAudioRecorder *)recorder successfully:(BOOL)flag {
    NSLog(@"Recording done. Sending and restarting...");
    NSURL *url = [NSURL fileURLWithPath: recordingFilePath];
    NSError *err = nil;
    NSData *audioData = [NSData dataWithContentsOfFile:[url path] options: 0 error:&err];
        
    RKObjectManager* om = [RKObjectManager sharedManager];
//    NSLog(@"%@",om.baseURL);
    RKParams* params = [RKParams params];
    // submit audio file in post
    [params setData:audioData MIMEType:@"audio/x-wav" forParam:@"recording"];
    NSLog(@"%@",contentMode);
    NSString* urlstring = [NSString stringWithFormat:@"/audio/?mode=%@",contentMode];
    [params setValue:@"mode" forParam:contentMode];
    [om.client post:urlstring params:params delegate:self];

    [self.recorder deleteRecording];
    [self makeNewRecorderAndRecord];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

-(void) request:(RKRequest *)request didFailLoadWithError:(NSError *)error {
    NSLog(@"%@",error.description);
}

-(void) request:(RKRequest *)request didLoadResponse:(RKResponse *)response {
    NSLog(@"RESPONSE LOADED: \n\n  %@",response.bodyAsString);
    
    if ([request.URL.absoluteString rangeOfString:self.contentMode].location == NSNotFound) {
        return;
    }
    
    if ([response.bodyAsString rangeOfString:@"failed"].location != NSNotFound) {
        return;
    }
    
    replacementWebView = [[UIWebView alloc] initWithFrame:CGRectMake([modes indexOfObject:contentMode]*1024, 0, 1024, 768)];
    replacementWebView.delegate = self;
    [replacementWebView setUserInteractionEnabled:NO];
    [replacementWebView loadHTMLString:response.bodyAsString baseURL:[NSURL URLWithString:@"http://"]];
    [scrollView addSubview:replacementWebView];
    [scrollView bringSubviewToFront:replacementWebView];
    [scrollView bringSubviewToFront:webView];
//    [webView removeFromSuperview];
//    //    [self.view addSubview:newWebView];
//    [webView loadHTMLString:response.bodyAsString baseURL:[NSURL URLWithString:@"http://"]];
//
  
    
//    [self.view addSubview:newView];
//    [webView loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"http://en.wikipedia.org/wiki/Special:Random"]]];

}

-(void)webViewDidFinishLoad:(UIWebView *)newWebView {
    NSLog(@"didfinishloading");
    if (!replacementWebView) {
        return;
    }
    
    CATransition *animation = [CATransition animation];
    [animation setDelegate:self];
    [animation setDuration:0.5f];
    animation.startProgress = 0;
    animation.endProgress   = 1; 
    [animation setTimingFunction:[CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut]];
    [animation setType:@"crossfade"];
    [animation setSubtype:kCATransitionFade];
    [animation setDelegate:self];
    
    [animation setRemovedOnCompletion:NO];
    //    [animation setFillMode: @"extended"];
    [[self.scrollView layer] addAnimation:animation forKey:@"crossfade"]; 
//    webView.alpha = 0;
    [UIView beginAnimations:@"crossfade" context:nil];
    [UIView setAnimationDuration:0.2];
    [UIView setAnimationCurve:UIViewAnimationCurveEaseInOut];
    [UIView commitAnimations];  
}


-(void)animationDidStop:(CAAnimation *)anim finished:(BOOL)flag {
    // clean up the old webview
    [webView removeFromSuperview];
    webView = replacementWebView;
    replacementWebView = nil;
}

-(void)scrollViewDidEndDecelerating:(UIScrollView *)tscrollView {
    NSLog(@"%f",tscrollView.contentOffset.x);
    contentMode = [modes objectAtIndex:((int)(tscrollView.contentOffset.x/1024))];
}

@end
